# Level System

`GamificationLevelRule` stores versioned minimum-XP thresholds. Level lookup
uses the greatest configured threshold not exceeding verified XP. If no rules
are configured, the safe default is level 1; no level is inferred from client
activity.
