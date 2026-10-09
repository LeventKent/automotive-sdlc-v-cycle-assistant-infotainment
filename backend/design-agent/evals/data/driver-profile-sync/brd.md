# Business Requirements Document (BRD) - Driver Profile Sync

Version: 0.4 (Draft)
Status: In review

## 1. Business Objectives
- BO-1: Let drivers carry their seat, mirror, climate, and media preferences between vehicles of the brand, including rental and shared fleet vehicles.
- BO-2: Increase connected-services subscription retention. Target: TBD (Marketing to provide).

## 2. Use Cases

### UC-1: Sign in to a vehicle
- Trigger: The driver signs in on the center display using the companion phone app (QR code).
- Flow: The vehicle downloads the driver's profile and applies infotainment and comfort preferences.
- Success: Preferences are applied before the vehicle starts moving.

### UC-2: Update preferences
- Trigger: The driver changes a preference in the vehicle.
- Flow: The change is uploaded to the cloud profile.
- Success: The change is available in the next vehicle the driver signs in to.

### UC-3: Sign out and wipe
- Trigger: The driver signs out, or the vehicle is returned to the fleet operator.
- Flow: All personal data of the driver is removed from the vehicle.
- Success: No personal data of the driver remains on the vehicle.

## 3. Business Rules
- BR-1: Seat and mirror positions are applied only while the gear is P.
- BR-2: Profile data is personal data under GDPR. Data residency requirements per market: TBD (Legal).
- BR-3: Conflict resolution when two vehicles change the same preference offline: To be determined.

## 4. Constraints
- C-1: Team size: TBD.
- C-2: Timeline: must align with the next platform release. Exact date TBD.
- C-3: Budget: not yet approved.

## 5. Open Issues
- OI-1: Is the cloud backend owned by this project or by the Connected Services team?
- OI-2: Are fleet operators allowed to pre-provision profiles?
