# Business Requirements Document (BRD) - Tire Pressure Monitoring Display

Version: 2.1
Status: Approved

## 1. Business Objectives
- BO-1: Replace the instrument-cluster-only TPMS warning with a combined cluster and center-display experience that shows per-wheel pressure and temperature.
- BO-2: Meet UNECE Regulation No. 141 (TPMS) and FMVSS 138 warning presentation requirements in all launch markets.
- BO-3: Reduce warranty claims for "unexplained TPMS warning" by 30% through clearer per-wheel information.

## 2. Use Cases

### UC-1: Low pressure warning while driving
- Trigger: The TPMS ECU reports that one or more tires are below the warning threshold.
- Flow: The cluster shows the regulated TPMS tell-tale. The center display shows a warning card that identifies the affected wheel(s).
- Success: The driver can identify which tire is affected at a glance.

### UC-2: Check tire pressures when parked
- Trigger: The driver opens the Vehicle > Tires screen while the vehicle is parked.
- Flow: The app shows pressure and temperature for each wheel and the recommended cold pressure for the current load setting.
- Success: The driver can adjust pressure at a gas station without consulting the manual.

### UC-3: Sensor fault
- Trigger: A wheel sensor stops reporting or reports an implausible value.
- Flow: The affected wheel shows "--" and a sensor fault message. The cluster tell-tale behaviour follows the TPMS ECU state.
- Success: A sensor fault is never shown as a valid pressure value.

## 3. Business Rules
- BR-1: The center display warning is supplementary. The regulated tell-tale in the instrument cluster is owned by the cluster software and is out of scope for this project.
- BR-2: Pressure is displayed in kPa, bar, or psi according to the vehicle unit setting.
- BR-3: The warning card cannot be permanently disabled by the user. It may be minimized, but it reappears on every ignition cycle while the fault persists.

## 4. Safety
- S-1: The HARA (document HARA-TPMS-004) assigns ASIL A to hazard HZ-12, "driver not informed of a significant pressure loss". The safety goal SG-12 is: "A low pressure condition reported by the TPMS ECU shall be indicated to the driver".
- S-2: The center-display presentation of SG-12 is allocated ASIL A. The per-wheel detail view (UC-2) is QM.

## 5. Constraints
- C-1: Team of 2 Kotlin engineers and 1 functional safety engineer (part time).
- C-2: Software freeze 6 months prior to SOP.
- C-3: Budget is limited to $60,000, including the ASIL A safety case work.
- C-4: The application consumes TPMS data only; it never sends commands to the TPMS ECU.
