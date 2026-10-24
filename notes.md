**START**

*2026-10-21: The objective of the project is to create a system which tracks equipment and service periods, stores the information in a database, and reports what's approaching or overdue. 

Decided that the system will track traditional industrial assets, including motors, pumps, generators, transformers, HVAC units, and boilers. For each asset, the fields that need to be defined are its specific ID, type, description, location, commissioning date, service intervals, last serviced date, and status.

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

Next, I created the [assets.csv](https://github.com/alissamaharaj/due-diligence/blob/main/data/assets.csv) with the data for the `Assets` table. It includes clean and bad rows, including blank fields, deviations from ISO date standard, duplicate IDs, invalid status options, and non-existent linked assets. The expected output table should look like this.
<img width="646" height="371" alt="Screenshot 2026-10-21 141003" src="https://github.com/user-attachments/assets/2615adf3-ac7f-4084-ae30-8512d0b79240" />

Then I did the same for the `Procedures`, `Frequencies`, and `Service History` tables.
The expected output tables should look like these:

Procedures

<img width="373" height="368" alt="Screenshot 2026-10-21 174034" src="https://github.com/user-attachments/assets/ebf37722-2901-4cac-9488-72c47b462f55" />
<img width="374" height="116" alt="Screenshot 2026-10-21 174113" src="https://github.com/user-attachments/assets/e7d7c265-1a06-4629-8125-daae6bd0a8e4" />

Frequencies

<img width="236" height="141" alt="Screenshot 2026-10-21 174133" src="https://github.com/user-attachments/assets/350a3b33-01b1-484b-9eb6-8edc3b97141b" />

Service History

<img width="418" height="371" alt="Screenshot 2026-10-21 174153" src="https://github.com/user-attachments/assets/246e663f-2253-4196-9450-2e02937cf752" />
<img width="416" height="139" alt="Screenshot 2026-10-21 174203" src="https://github.com/user-attachments/assets/741c363f-cd33-43d0-adaf-2fdcbd759daf" />

Next, I created the [loaders](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) for the `.csv` files, starting with `frequencies.csv`. 

I used notebooks for the first time to build this and had some struggles figuring out kernel configuration and such; I couldn't get it to run the code cells. It turns out I just needed to refresh the notebook after installing the kernel properly. 

Once I got that working, it was onto the fun part of building the loader. The next hitch I ran into was getting the file path to work since notebooks run from the `notebooks/` folder, so I had to learn the correct notation to direct the file path. `../data/frequencies.csv`. When that was done, I wrote the rest of the code. `load_frequencies()` reads the file into a dictionary, converting the service intervals from strings to integers, and gives this sample output: `{'weekly': 7, 'monthly': 30, 'quarterly': 90, 'annually': 365}`. This was the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/01-load-frequencies.ipynb) used.

*2026-10-22: Next, I created the loader for the `assets.csv`. This one was significantly more complex, so it took a lot of trial and error. I needed it to not only load the file and read it into a dictionary, but also to parse the data, differentiate between the clean lines and the bad ones, and sort them into two lists based on one reason for failure per row; the criteria were:
  - blank fields
  - invalid commissioning_date
  - invalid status
  - type does not match id_type
  - duplicate asset_id

Firstly, I included a block to look through the information fields using a list to name them (excluding linked_asset_id), and identify the row as bad if any of the other fields' values contained only blank spaces. Then, a block to convert the commissioning_date string into a datetime object in the ISO date format `YYYY-MM-DD`; if the commissioning_date is in an invalid format, this would return a `ValueError` and then identify the row as bad. After that, a block to pick out invalid status values by comparing them to a list of `VALID_STATUS` values. To identify non-matching asset_id and type fields, I needed to split the asset_id and use the prefix to match to a preset list of `prefix:type` pairs; if they did not match, the row was identified as bad once again. Lastly, duplicate asset_id values were identified by adding the asset_id values to a set as they were looped through; the asset_id values were only added to the set if they were not already present; if it was already present, this identified the row as bad. The checks were ordered this way so that the first failure is the one recorded and that each row is allowed only one failure.

Some issues I had while building this part: there was an instance of a stray comma turning an assignment statement into an accidental tuple, and a bigger issue I had was the final lists having way too many values in them, which took me a while to realize was because my append lines were within a loop, which was causing the lists to have values committed individually instead of by row.

The identified clean rows were added to a good rows list, and the bad rows were added to a rejected rows list, along with the row number (relative to the header row being 1) and the reason for the row failing, indicated by a string explanation.

The sample output of this is `8 good rows
5 rejected rows
rejected lines:
9
10
11
12
14`.

This was the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/02-load-assets.ipynb) used.

Next was the second pass through this code to introduce checks on the linked_asset_id column, since it was excluded from the first pass as it could constitute a bad row for more than one failure. This included assigning the row to the rejected rows if:
  - the linked asset_id does not exist
  - the linked asset was not part of a `pump:motor` (vice versa) pair
  - the linked asset's linked asset_id did not point back to the original row

I chose to include that linked assets are stored on both sides, not one, to avoid having an additional lookup step if only one asset is checked.

`PMP-001`'s linked asset was set to `MTR-001` so that the pair was reciprocated and some new lines were also added to the asset.csv to exercise these rules.

The sample output after these updates is this `7 good rows
8 rejected rows
rejected rows:
9 blank location
10 invalid commissioning_date
11 duplicate asset_id
12 invalid status
13 linked asset not found
14 type does not match id_type
15 link must pair a motor and a pump
16 link not reciprocated`

The `load_assets()` function was moved to the [loaders](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) file, alongside the `load_frequencies()` function and returns the good and rejected rows.
