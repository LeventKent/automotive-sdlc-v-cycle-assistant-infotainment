# Business Requirements Document (BRD) - EV Charging Planner

Version: 1.0
Status: Approved

## 1. Business Objectives
- BO-1: Reduce range anxiety for owners of the battery-electric model line by planning charging stops automatically.
- BO-2: Increase use of partner charging networks to at least 40% of all public charging sessions within 12 months of launch.
- BO-3: Reduce support calls related to "stranded vehicle" events by 25% in the first year.

## 2. Stakeholders
| Stakeholder | Interest |
|---|---|
| Product Owner, EV Services | Feature scope, partner KPIs |
| Charging Partnerships | Network coverage, pricing display |
| Vehicle Software Platform | AAOS integration, VHAL access |
| Customer Support | Fewer stranded-vehicle cases |

## 3. Use Cases

### UC-1: Plan a trip with charging stops
- Trigger: Driver sets a navigation destination that is beyond the current estimated range.
- Flow: The app reads the current state of charge, calculates the route energy demand, and proposes charging stops along the route.
- Success: The driver accepts the plan with a single tap or a voice confirmation.

### UC-2: Re-plan when conditions change
- Trigger: State of charge drops faster than predicted, or a planned charger becomes unavailable.
- Flow: The app recalculates the plan and informs the driver with a short audio prompt and a single-tap card.
- Success: The new plan is shown without the driver having to open the app.

### UC-3: Check charger availability before arrival
- Trigger: The vehicle is 15 minutes away from a planned charger.
- Flow: The app queries live availability and connector status.
- Success: If the charger is occupied or out of service, an alternative is offered.

## 4. Business Rules
- BR-1: Only chargers with a connector compatible with the vehicle (CCS2) are proposed.
- BR-2: The plan must keep a minimum arrival state of charge of 10% at every stop and at the destination.
- BR-3: Partner network chargers are preferred when the detour is under 5 km.
- BR-4: Prices are displayed in the local currency as provided by the charging network; the app does not process payments.

## 5. Constraints and Assumptions
- C-1: Development team of 3 engineers (2 Android Automotive, 1 backend).
- C-2: The feature must be ready 8 months prior to SOP.
- C-3: Budget is limited to $40,000 including charging network API licensing.
- C-4: The application is classified as QM (quality managed) per the item definition and HARA; no ASIL is allocated to this application. It must not write to any vehicle control signal.
- A-1: The charging network provides an OCPI 2.2.1 compatible API.
- A-2: The vehicle exposes state of charge and estimated range through VHAL properties.

## 6. Success Metrics
- 90% of trips beyond range are completed with an accepted plan.
- Fewer than 1% of planned stops result in arrival below 10% state of charge.
