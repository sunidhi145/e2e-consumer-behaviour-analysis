SEGMENT_METADATA = {
    "VIP_Wealth_Builders": {
        "icon": "diamond",
        "profile": "High-value customers with high balances, long account tenure, several active products, strong financial stability, and minimal overdraft activity.",
        "business_value": "Most valuable and loyal customers with strong potential for wealth management, investment products, premium banking, and relationship management.",
        "actions": [
            "Assign a relationship manager",
            "Offer investment advisory",
            "Promote premium banking tiers",
            "Invite to exclusive banking events",
            "Cross-sell wealth products",
        ],
    },
    "Active_Spenders": {
        "icon": "zap",
        "profile": "Highly engaged customers with frequent transactions, moderate balances, moderate transaction sizes, and growing engagement.",
        "business_value": "Strong potential for premium cards, suitable credit products, loan offers, and cross-selling.",
        "actions": [
            "Offer premium credit cards",
            "Provide suitable credit-limit upgrades",
            "Offer loan pre-approvals",
            "Promote savings and investment education",
            "Run loyalty campaigns",
        ],
    },
    "Dormant_At_Risk": {
        "icon": "alert",
        "profile": "Low-activity customers with low balances, high inactivity, longer transaction gaps, overdraft stress, or potential churn risk.",
        "business_value": "Retention and risk-management opportunity.",
        "actions": [
            "Launch re-engagement campaigns",
            "Offer financial wellness support",
            "Offer overdraft protection",
            "Provide win-back incentives",
            "Monitor account closure risk",
        ],
    },
    "Young_Savers": {
        "icon": "leaf",
        "profile": "Newer and relatively low-risk customers with smaller transactions, fewer active products, conservative activity, and long-term growth potential.",
        "business_value": "Future lifetime-value and onboarding opportunity.",
        "actions": [
            "Offer starter investment products",
            "Provide savings-goal tools",
            "Deliver financial education",
            "Promote micro-investing",
            "Focus on long-term retention",
        ],
    },
    "Business_Owners": {
        "icon": "briefcase",
        "profile": "High-volume customers with large or irregular transactions, high transaction frequency, multiple products, and business-oriented banking behaviour.",
        "business_value": "Strong opportunity for business credit, working-capital products, treasury management, and business banking services.",
        "actions": [
            "Offer business banking packages",
            "Provide B2B credit lines",
            "Offer invoice financing",
            "Promote treasury services",
            "Assign a business account manager",
        ],
    },
}


def get_metadata(segment):
    return SEGMENT_METADATA.get(
        str(segment),
        {
            "icon": "circle",
            "profile": "No curated profile metadata is available for this segment.",
            "business_value": "Review available feature patterns before assigning a business strategy.",
            "actions": ["Review feature averages", "Validate segment assignment", "Monitor customer behaviour"],
        },
    )
