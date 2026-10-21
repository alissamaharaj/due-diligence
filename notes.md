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

To define service intervals, it must be considered that service for industrial assets usually entails multiple procedures scheduled at differing intervals rather than service being a single event at regular intervals. To avoid unnecessary complexity, I decided to pick a few procedures per asset type based on researching typical maintenance procedures carried out for each and restrict it to weekly, monthly, quarterly, and annual service periods.
  - `MTR` - inspection (weekly), bearing lubrication (monthly), alignment (quarterly), overhaul (annual)
  - `PMP` - inspection (weekly), vibration analysis (monthly), instrument calibration (quarterly), overhaul (annual)
  - `GEN` - inspection (weekly), belt service (monthly), coolant replacement (quarterly), overhaul (annual)
  - `TRN` - inspection (weekly), oil level (monthly), thermal scan (quarterly), overhaul (annual)
  - `HVC` - inspection (weekly), filter service (monthly), line service (quarterly), overhaul (annual)
  - `BLR` - inspection (weekly), sample water (monthly), trip interlocks (quarterly), overhaul (annual)

Defining service intervals in days, weekly = 7, monthly = 30, quarterly = 90, and annually = 365.

Next, I sketched out the tables that would make up the database; these are the `Assets`, `Procedures`, and `Service History` tables

**Assets**
| ID | Type | Description | Location | Commissioning Date | Status | Linked Asset ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|  |  |  |  |  |  |  |

Linked assets are those that drive or are driven by each other; for example, pump and motor pairs.

Status values: `active`, `under repair`, `decommissioned`

**Procedures**
| Procedure ID | Asset ID | Description | Service Frequency |
| :--- | :--- | :--- | :--- |
|  |  |  |  |

Procedure ID will follow `XXX-000-P0` structure, where `XXX-000` is the Asset ID.

Service frequency will be listed as weekly, monthly, quarterly, or annually; to have the interval in days available for querying purposes, this small linked lookup table will be used.

**Frequencies**
| Service Frequency | Service Interval (days) |
| :--- | :--- |
| weekly | 7 |
| monthly | 30 |
| quarterly | 90 |
| annually | 365 |

**Service History**
| Record ID | Procedure ID | Date Completed | Notes |
| :--- | :--- | :--- | :--- |
|  |  |  |  |

Planning the query parameters for the system:
  - How many of each asset type?
  - What is due next?
  - What is overdue?
  - What is due in x number of days?
  - Where are the most overdue items?
  - What assets are linked?
  - Service history for individual items

To answer these, three charts will be generated:
  - Overdue procedures by asset type
  - Overdue procedures by location
  - Services completed by month

Next, I created the [assets.csv](https://github.com/alissamaharaj/due-diligence/blob/main/data/assets.csv) with the data for the `Assets` table. It includes clean and bad rows. The expected output table should look like this.
<img width="646" height="371" alt="Screenshot 2026-10-21 141003" src="https://github.com/user-attachments/assets/2615adf3-ac7f-4084-ae30-8512d0b79240" />
