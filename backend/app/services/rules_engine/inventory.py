"""
Inventory Rules Engine

Rule-based logic for detecting cost leakages in inventory data.
Contains:
1. Overstocking - Items with excessive days on hand
2. Expiry Risk - Items expiring soon with significant quantity/value
"""

import logging
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.inventory import InventoryData
from app.models.finding import Finding

logger = logging.getLogger(__name__)


# Configuration thresholds
OVERSTOCK_DAYS_THRESHOLD = 90  # Days on hand above this = overstock
EXPIRY_DAYS_THRESHOLD = 30     # Items expiring within 30 days


def run_overstocking_rule(db: Session) -> List[Finding]:
    """
    Rule 3: Overstocking
    
    Logic:
    - Calculate days_on_hand = quantity_on_hand / daily_usage_rate
    - If days_on_hand > 90 (configurable), flag as Overstock
    
    Insight: "Item X has 180 days of inventory on hand. Consider reducing orders."
    
    Returns:
        List of Finding objects to be persisted
    """
    logger.info("Running Overstocking rule...")
    findings = []
    
    # Get all inventory items with usage rate data
    inventory_items = (
        db.query(InventoryData)
        .filter(
            InventoryData.daily_usage_rate.isnot(None),
            InventoryData.daily_usage_rate > 0,
            InventoryData.quantity_on_hand > 0
        )
        .all()
    )
    
    logger.info(f"Analyzing {len(inventory_items)} items with usage data")
    
    for item in inventory_items:
        # Calculate days on hand
        days_on_hand = item.quantity_on_hand / item.daily_usage_rate
        
        if days_on_hand > OVERSTOCK_DAYS_THRESHOLD:
            # Calculate potential tied-up capital
            tied_up_value = 0
            if item.unit_cost:
                # Consider optimal stock level as 45 days
                optimal_qty = item.daily_usage_rate * 45
                excess_qty = item.quantity_on_hand - optimal_qty
                if excess_qty > 0:
                    tied_up_value = excess_qty * item.unit_cost
            
            # Determine severity
            if days_on_hand > 180:
                severity = "high"
            elif days_on_hand > 120:
                severity = "medium"
            else:
                severity = "low"
            
            finding = Finding(
                category="overstock",
                severity=severity,
                description=(
                    f"SKU {item.sku} has {days_on_hand:.0f} days of inventory on hand "
                    f"({item.quantity_on_hand:.0f} units at {item.daily_usage_rate:.1f}/day). "
                    f"Consider reducing stock to avoid tied-up capital."
                    + (f" Location: {item.location}." if item.location else "")
                ),
                potential_savings=round(tied_up_value, 2) if tied_up_value > 0 else None
            )
            findings.append(finding)
            logger.info(f"Found overstock: {item.sku} with {days_on_hand:.0f} days on hand")
    
    logger.info(f"Overstocking rule complete. Found {len(findings)} issues.")
    return findings


def run_expiry_risk_rule(db: Session) -> List[Finding]:
    """
    Rule 4: Expiry Risk
    
    Logic:
    - If expiry_date - today < 30 days AND quantity > 0, flag as Expiry Risk
    - Calculate potential loss based on unit_cost * quantity
    
    Insight: "$5k worth of reagents expiring in 2 weeks."
    
    Returns:
        List of Finding objects to be persisted
    """
    logger.info("Running Expiry Risk rule...")
    findings = []
    
    today = datetime.now().date()
    expiry_threshold = today + timedelta(days=EXPIRY_DAYS_THRESHOLD)
    
    # Get items expiring within threshold
    expiring_items = (
        db.query(InventoryData)
        .filter(
            InventoryData.expiry_date.isnot(None),
            InventoryData.expiry_date <= expiry_threshold,
            InventoryData.expiry_date >= today,  # Not already expired
            InventoryData.quantity_on_hand > 0
        )
        .all()
    )
    
    logger.info(f"Found {len(expiring_items)} items expiring within {EXPIRY_DAYS_THRESHOLD} days")
    
    for item in expiring_items:
        days_until_expiry = (item.expiry_date - today).days
        
        # Calculate potential loss
        potential_loss = 0
        if item.unit_cost:
            potential_loss = item.quantity_on_hand * item.unit_cost
        
        # Determine severity based on days until expiry and value
        if days_until_expiry <= 7:
            severity = "high"
        elif days_until_expiry <= 14:
            severity = "medium"
        else:
            severity = "low"
        
        # Upgrade severity if high value at stake
        if potential_loss > 1000:
            severity = "high"
        
        finding = Finding(
            category="expiry_risk",
            severity=severity,
            description=(
                f"SKU {item.sku} expires in {days_until_expiry} days ({item.expiry_date}). "
                f"{item.quantity_on_hand:.0f} units at risk"
                + (f" valued at ${potential_loss:.2f}." if potential_loss > 0 else ".")
                + (f" Location: {item.location}." if item.location else "")
            ),
            potential_savings=round(potential_loss, 2) if potential_loss > 0 else None
        )
        findings.append(finding)
        logger.info(f"Found expiry risk: {item.sku} expires in {days_until_expiry} days")
    
    # Also check for already expired items
    expired_items = (
        db.query(InventoryData)
        .filter(
            InventoryData.expiry_date.isnot(None),
            InventoryData.expiry_date < today,
            InventoryData.quantity_on_hand > 0
        )
        .all()
    )
    
    for item in expired_items:
        potential_loss = 0
        if item.unit_cost:
            potential_loss = item.quantity_on_hand * item.unit_cost
        
        finding = Finding(
            category="expiry_risk",
            severity="high",
            description=(
                f"SKU {item.sku} has EXPIRED ({item.expiry_date}). "
                f"{item.quantity_on_hand:.0f} units need immediate disposal"
                + (f" - loss of ${potential_loss:.2f}." if potential_loss > 0 else ".")
            ),
            potential_savings=round(potential_loss, 2) if potential_loss > 0 else None
        )
        findings.append(finding)
        logger.info(f"Found expired item: {item.sku}")
    
    logger.info(f"Expiry Risk rule complete. Found {len(findings)} issues.")
    return findings


def run_all_inventory_rules(db: Session) -> List[Finding]:
    """
    Execute all inventory rules and return combined findings.
    """
    logger.info("=== Starting Inventory Rules Engine ===")
    
    all_findings = []
    
    # Rule 3: Overstocking
    all_findings.extend(run_overstocking_rule(db))
    
    # Rule 4: Expiry Risk
    all_findings.extend(run_expiry_risk_rule(db))
    
    logger.info(f"=== Inventory Rules Complete: {len(all_findings)} total findings ===")
    return all_findings
