
"""OpenRelief: transparent donation allocation engine."""

import pandas as pd


STOCK_COLUMNS = {"item", "quantity"}
NEED_COLUMNS = {
    "recipient",
    "item",
    "needed",
    "already_has",
    "priority",
    "max_can_receive",
}


def prepare_inputs(stock, needs):
    """Validate and clean donation stock and recipient needs."""
    stock = stock.copy()
    needs = needs.copy()

    missing_stock = STOCK_COLUMNS - set(stock.columns)
    missing_needs = NEED_COLUMNS - set(needs.columns)

    if missing_stock:
        raise ValueError(
            f"Stock is missing columns: {', '.join(sorted(missing_stock))}"
        )

    if missing_needs:
        raise ValueError(
            f"Needs are missing columns: {', '.join(sorted(missing_needs))}"
        )

    if stock.empty:
        raise ValueError("Enter at least one available resource.")

    if needs.empty:
        raise ValueError("Enter at least one recipient need.")

    stock["item"] = stock["item"].astype("string").str.strip()
    needs["item"] = needs["item"].astype("string").str.strip()
    needs["recipient"] = needs["recipient"].astype("string").str.strip()

    if (
        stock["item"].isna().any()
        or (stock["item"] == "").any()
        or needs["item"].isna().any()
        or (needs["item"] == "").any()
        or needs["recipient"].isna().any()
        or (needs["recipient"] == "").any()
    ):
        raise ValueError("Item names and recipient names cannot be blank.")

    numeric_columns = {
        "stock": ["quantity"],
        "needs": [
            "needed",
            "already_has",
            "priority",
            "max_can_receive",
        ],
    }

    try:
        for column in numeric_columns["stock"]:
            stock[column] = pd.to_numeric(stock[column], errors="raise")

        for column in numeric_columns["needs"]:
            needs[column] = pd.to_numeric(needs[column], errors="raise")
    except (ValueError, TypeError):
        raise ValueError("All quantities and priorities must be numbers.")

    for column in numeric_columns["stock"]:
        values = stock[column]
        if (
            values.isna().any()
            or (~values.map(lambda x: pd.notna(x) and float(x) >= 0)).any()
            or (values % 1 != 0).any()
        ):
            raise ValueError(
                f"{column} must contain non-negative whole numbers."
            )

    for column in ["needed", "already_has", "max_can_receive"]:
        values = needs[column]
        if (
            values.isna().any()
            or (values < 0).any()
            or (values % 1 != 0).any()
        ):
            raise ValueError(
                f"{column} must contain non-negative whole numbers."
            )

    if (
        needs["priority"].isna().any()
        or (needs["priority"] % 1 != 0).any()
        or (~needs["priority"].between(1, 5)).any()
    ):
        raise ValueError("Priority must be a whole number from 1 to 5.")

    stock["quantity"] = stock["quantity"].astype(int)
    needs["needed"] = needs["needed"].astype(int)
    needs["already_has"] = needs["already_has"].astype(int)
    needs["priority"] = needs["priority"].astype(int)
    needs["max_can_receive"] = needs["max_can_receive"].astype(int)

    # Combine repeated stock entries for the same item.
    stock = stock.groupby("item", as_index=False)["quantity"].sum()

    return stock, needs


def allocate_resources(stock, needs, strategy="need-based"):
    """Allocate resources without exceeding stock or recipient limits.

    Strategies:
    - need-based: higher-priority recipients are considered first.
    - equal-distribution: available units are shared in rounds.
    """
    stock, needs = prepare_inputs(stock, needs)

    strategy = strategy.lower().replace("_", "-").strip()
    if strategy not in {"need-based", "equal-distribution"}:
        raise ValueError(
            "Strategy must be 'need-based' or 'equal-distribution'."
        )

    results = []

    for item in needs["item"].drop_duplicates():
        item_needs = needs[needs["item"] == item].copy().reset_index(
            names="original_order"
        )

        available_row = stock.loc[stock["item"] == item, "quantity"]
        available = int(available_row.sum()) if not available_row.empty else 0

        item_needs["shortage"] = (
            item_needs["needed"] - item_needs["already_has"]
        ).clip(lower=0)

        item_needs["allocation_limit"] = item_needs[
            ["shortage", "max_can_receive"]
        ].min(axis=1)

        item_needs["allocated"] = 0

        if strategy == "need-based":
            order = item_needs.sort_values(
                ["priority", "allocation_limit", "original_order"],
                ascending=[False, False, True],
            ).index

            for idx in order:
                amount = min(
                    available,
                    int(item_needs.at[idx, "allocation_limit"]),
                )
                item_needs.at[idx, "allocated"] = amount
                available -= amount

                if available == 0:
                    break

        else:
            # Fair rounds: each eligible recipient gets one unit per turn.
            while available > 0:
                eligible = item_needs.index[
                    item_needs["allocated"] < item_needs["allocation_limit"]
                ].tolist()

                if not eligible:
                    break

                for idx in eligible:
                    if available == 0:
                        break

                    item_needs.at[idx, "allocated"] += 1
                    available -= 1

        item_needs["unmet_after_allocation"] = (
            item_needs["shortage"] - item_needs["allocated"]
        ).clip(lower=0)

        item_needs["leftover_stock_for_item"] = available

        results.append(item_needs)

    result = pd.concat(results, ignore_index=True)

    result = result.rename(
        columns={
            "recipient": "Recipient",
            "item": "Item",
            "needed": "Requested",
            "already_has": "Already has",
            "shortage": "Shortage before allocation",
            "priority": "Priority",
            "max_can_receive": "Maximum they can receive",
            "allocated": "Allocated",
            "unmet_after_allocation": "Unmet need",
            "leftover_stock_for_item": "Leftover stock",
        }
    )

    output_columns = [
        "Recipient",
        "Item",
        "Requested",
        "Already has",
        "Shortage before allocation",
        "Priority",
        "Maximum they can receive",
        "Allocated",
        "Unmet need",
        "Leftover stock",
    ]

    return result[output_columns]

