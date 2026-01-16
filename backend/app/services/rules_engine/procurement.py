"""
Procurement Rules Engine

Rule-based logic for detecting cost leakages in procurement data.
Contains:
1. Vendor Price Variance - Same SKU priced differently across vendors
2. Contract vs Invoice Mismatch - Invoice price exceeds contract price
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.procurement import ProcurementData
from app.models.finding import Finding

logger = logging.getLogger(__name__)


# Configuration thresholds
PRICE_VARIANCE_THRESHOLD = 0.10  # 10% threshold for flagging price differences


def run_vendor_price_variance(db: Session) -> List[Finding]:
    """
    Rule 1: Vendor Price Variance
    
    Logic:
    - Group purchases by SKU
    - Calculate the mean unit price for each SKU
    - Flag any purchase where unit_price > mean_price + threshold (10%)
    
    Insight: "You paid $50 for Syringe X from Vendor A but $40 from Vendor B"
    
    Returns:
        List of Finding objects to be persisted
    """
    logger.info("Running Vendor Price Variance rule...")
    findings = []
    
    # Step 1: Get all procurement data grouped by SKU with price stats
    sku_stats = (
        db.query(
            ProcurementData.item_sku,
            func.avg(ProcurementData.unit_price).label("avg_price"),
            func.min(ProcurementData.unit_price).label("min_price"),
            func.max(ProcurementData.unit_price).label("max_price"),
            func.count(ProcurementData.id).label("count")
        )
        .group_by(ProcurementData.item_sku)
        .having(func.count(ProcurementData.id) > 1)  # Only SKUs with multiple purchases
        .all()
    )
    
    logger.info(f"Found {len(sku_stats)} SKUs with multiple purchases")
    
    # Step 2: For each SKU with price variance, find overpriced purchases
    for sku_stat in sku_stats:
        sku = sku_stat.item_sku
        avg_price = sku_stat.avg_price
        min_price = sku_stat.min_price
        max_price = sku_stat.max_price
        
        # Check if there's significant variance
        price_variance_pct = (max_price - min_price) / avg_price if avg_price > 0 else 0
        
        if price_variance_pct > PRICE_VARIANCE_THRESHOLD:
            # Find the overpriced purchases (above average + threshold)
            threshold_price = avg_price * (1 + PRICE_VARIANCE_THRESHOLD)
            
            overpriced = (
                db.query(ProcurementData)
                .filter(
                    ProcurementData.item_sku == sku,
                    ProcurementData.unit_price > threshold_price
                )
                .all()
            )
            
            for item in overpriced:
                # Calculate potential savings
                overpayment = item.unit_price - avg_price
                total_savings = overpayment * item.quantity
                
                # Determine severity based on overpayment percentage
                overpayment_pct = overpayment / avg_price * 100
                if overpayment_pct > 25:
                    severity = "high"
                elif overpayment_pct > 15:
                    severity = "medium"
                else:
                    severity = "low"
                
                finding = Finding(
                    category="price_variance",
                    severity=severity,
                    description=(
                        f"SKU {sku} purchased from {item.vendor_name} at ${item.unit_price:.2f} "
                        f"is {overpayment_pct:.1f}% above average price of ${avg_price:.2f}. "
                        f"Lowest price available: ${min_price:.2f}."
                    ),
                    potential_savings=round(total_savings, 2)
                )
                findings.append(finding)
                logger.info(f"Found price variance: {sku} from {item.vendor_name}")
    
    logger.info(f"Vendor Price Variance rule complete. Found {len(findings)} issues.")
    return findings


def run_contract_mismatch(db: Session) -> List[Finding]:
    """
    Rule 2: Contract vs Invoice Mismatch
    
    Logic:
    - Find purchases where unit_price > contract_price
    - Flag as invoice overcharge
    
    Insight: "Vendor charged $120, contract rate is $100. Overcharge."
    
    Returns:
        List of Finding objects to be persisted
    """
    logger.info("Running Contract vs Invoice Mismatch rule...")
    findings = []
    
    # Find all records where invoice price exceeds contract price
    mismatches = (
        db.query(ProcurementData)
        .filter(
            ProcurementData.contract_price.isnot(None),
            ProcurementData.contract_price > 0,
            ProcurementData.unit_price > ProcurementData.contract_price
        )
        .all()
    )
    
    logger.info(f"Found {len(mismatches)} contract mismatches")
    
    for item in mismatches:
        overcharge = item.unit_price - item.contract_price
        overcharge_pct = (overcharge / item.contract_price) * 100
        total_savings = overcharge * item.quantity
        
        # Determine severity
        if overcharge_pct > 20:
            severity = "high"
        elif overcharge_pct > 10:
            severity = "medium"
        else:
            severity = "low"
        
        finding = Finding(
            category="contract_mismatch",
            severity=severity,
            description=(
                f"SKU {item.item_sku} from {item.vendor_name}: "
                f"Invoiced at ${item.unit_price:.2f} but contract price is ${item.contract_price:.2f}. "
                f"Overcharge of ${overcharge:.2f} ({overcharge_pct:.1f}%) per unit."
            ),
            potential_savings=round(total_savings, 2)
        )
        findings.append(finding)
        logger.info(f"Found contract mismatch: {item.item_sku} from {item.vendor_name}")
    
    logger.info(f"Contract Mismatch rule complete. Found {len(findings)} issues.")
    return findings


def run_all_procurement_rules(db: Session) -> List[Finding]:
    """
    Execute all procurement rules and return combined findings.
    """
    logger.info("=== Starting Procurement Rules Engine ===")
    
    all_findings = []
    
    # Rule 1: Vendor Price Variance
    all_findings.extend(run_vendor_price_variance(db))
    
    # Rule 2: Contract vs Invoice Mismatch
    all_findings.extend(run_contract_mismatch(db))
    
    logger.info(f"=== Procurement Rules Complete: {len(all_findings)} total findings ===")
    return all_findings
