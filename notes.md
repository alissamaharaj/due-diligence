**START**

*21-10-26: The objective of the project is to create a system which tracks equipment and service periods, stores the information in a database, and reports what's approaching or overdue. 

Decided that the system will track traditional industrial assets, including motors, pumps, generators, transformers, HVAC units, and boilers. For each asset, the fields that would need to be defined are its specific ID, type, description, location, commissioning date, service intervals, last serviced date, and status.

ID formats for each asset will follow `XXX-000` structure:
  - `MTR` - motors
  - `PMP` - pumps
  - `GEN` - generators
  - `TRN` - transformers
  - `HVC` - HVAC units
  - `BLR` - boilers

To define service intervals, it must be considered that service for industrial assets usually entails multiple procedures scheduled at differing intervals rather than service being a single event at regular intervals. To avoid unnecessary complexity, I decided to pick a few procedures per asset type and restrict it to weekly, monthly, quarterly, and annual service periods.
  - `MTR` - inspection (weekly), bearing lubrication (monthly), alignment (quarterly), overhaul (annual)
  - `PMP` - inspection (weekly), vibration analysis (monthly), calibration (quarterly), overhaul (annual)
  - `GEN` - inspection (weekly), belt service (monthly), coolant replacement (quarterly), overhaul (annual)
  - `TRN` - inspection (weekly), brush service (monthly), thermal scan (quarterly), overhaul (annual)
  - `HVC` - inspection (weekly), filter service (monthly), line service (quarterly), overhaul (annual)
  - `BLR` - inspection (weekly), sample water (monthly), trip interlocks (quarterly), overhaul (annual)


