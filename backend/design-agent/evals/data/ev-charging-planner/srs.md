# Software Requirements Specification (SRS) - EV Charging Planner

Version: 1.0
Platform: Android Automotive OS (AAOS) 14, Kotlin

## 1. Functional Requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-100 | The application shall read battery state of charge (VHAL property EV_BATTERY_LEVEL) and estimated range (VHAL property RANGE_REMAINING) at least once every 10 seconds while driving. | Must |
| FR-110 | The application shall compute a charging plan for any destination beyond the estimated range, keeping arrival state of charge at or above 10% at every stop. | Must |
| FR-120 | The application shall propose only CCS2 chargers. | Must |
| FR-130 | The application shall prefer partner network chargers when the detour is less than 5 km. | Should |
| FR-140 | The application shall query live charger availability through the OCPI 2.2.1 Locations module 15 minutes before arrival at a planned stop. | Must |
| FR-150 | The application shall re-plan when the measured consumption deviates from the prediction by more than 15% over a 20 km window, or when a planned charger becomes unavailable. | Must |
| FR-160 | The application shall hand the final route and waypoints to the system navigation app through the AAOS navigation intent; it shall not implement its own turn-by-turn guidance. | Must |
| FR-170 | The application shall support plan acceptance by single tap and by voice confirmation ("Yes, start the plan"). | Must |
| FR-180 | The application shall display charger prices as provided by the network, in local currency. It shall not process payments. | Should |

## 2. Non-Functional Requirements
| ID | Requirement | Target |
|---|---|---|
| NFR-100 | Plan computation latency | Initial plan within 3 seconds for routes up to 800 km (p95). |
| NFR-110 | Re-plan latency | Re-plan within 2 seconds (p95). |
| NFR-120 | Offline behaviour | If connectivity is lost, keep the last plan and mark availability data as stale with a timestamp. |
| NFR-130 | Resource usage | Memory below 120 MB; no foreground CPU use above 10% for more than 5 seconds. |
| NFR-140 | Security | All network calls over TLS 1.2 or higher; OCPI token stored in Android Keystore. |
| NFR-150 | Driver distraction | Comply with Android for Cars driver distraction guidelines: at most 6 list items while driving, no free-text input while driving. |
| NFR-160 | Safety classification | QM. The application has read-only access to vehicle properties and must not write any VHAL property. |

## 3. Interfaces
- IF-1: VHAL (read-only): EV_BATTERY_LEVEL, RANGE_REMAINING, PERF_VEHICLE_SPEED, GEAR_SELECTION.
- IF-2: OCPI 2.2.1 Locations and Tariffs modules over HTTPS, token authentication.
- IF-3: AAOS navigation intent for route handover.
- IF-4: Google Assistant app actions for voice confirmation.

## 4. Out of Scope
- Payment processing, charger reservation, and battery preconditioning control.
