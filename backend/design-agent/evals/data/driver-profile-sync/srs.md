# Software Requirements Specification (SRS) - Driver Profile Sync

Version: 0.4 (Draft)
Platform: Android Automotive OS (AAOS) 14, Kotlin

## 1. Functional Requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-100 | The application shall support sign-in by scanning a QR code with the companion app. | Must |
| FR-110 | The application shall download the profile and apply infotainment preferences (media sources, radio presets, display theme, language) after sign-in. | Must |
| FR-120 | The application shall request seat and mirror positions from the comfort ECU only while the gear is P. | Must |
| FR-130 | The application shall upload preference changes to the cloud profile. Upload frequency: TBD. | Must |
| FR-140 | The application shall delete all locally stored data of a driver on sign-out. | Must |
| FR-150 | The application shall resolve conflicting offline changes. Strategy: TBD. | Should |

## 2. Non-Functional Requirements
| ID | Requirement | Target |
|---|---|---|
| NFR-100 | Profile apply time after sign-in | TBD |
| NFR-110 | Security | Profile data encrypted at rest and in transit. Key management approach: TBD. |
| NFR-120 | Privacy | GDPR compliant. Data residency: TBD. |
| NFR-130 | Availability of the cloud profile service | TBD |

## 3. Interfaces
- IF-1: Cloud profile service REST API. Specification: PLACEHOLDER (not yet available).
- IF-2: Comfort ECU seat and mirror memory request through VHAL property SEAT_MEMORY_SET.
- IF-3: Companion phone app QR sign-in. Protocol: TBD.
