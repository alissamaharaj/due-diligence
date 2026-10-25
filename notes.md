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

Procedure ID will follow `XXX-000-P0` structure, where `XXX-000` is the Asset ID and `P0` is the Procedure tag.

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

Firstly, I included a block to look through the information fields using a list to name them (excluding linked_asset_id), and identify the row as bad if any of the other fields' values contained only blank spaces. Then, a block to convert the commissioning_date string into a datetime object in the ISO date format `YYYY-MM-DD`, assigned as `DATE_FMT`; if the commissioning_date is in an invalid format, this would return a `ValueError` and then identify the row as bad. After that, a block to pick out invalid status values by comparing them to a list of `VALID_STATUS` values. To identify non-matching asset_id and type fields, I needed to split the asset_id and use the prefix to match to a preset list of `prefix:type` pairs; if they did not match, the row was identified as bad once again. Lastly, duplicate asset_id values were identified by adding the asset_id values to a set as they were looped through; the asset_id values were only added to the set if they were not already present; if it was already present, this identified the row as bad. The checks were ordered this way so that the first failure is the one recorded and that each row is allowed only one failure.

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

The sample output after these updates is: 7 good rows
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

The `load_assets()` function was moved to the [loaders](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) file, alongside the `load_frequencies()` function, and returns the good and rejected rows.

*2026-10-24: Next was the loader for the `procedures.csv` file. This went a lot faster after having done the asset loader because I could just follow that framework there. The failure criteria for these rows were:
  - blank fields
  - invalid procedure tags
  - procedure_id does not match asset_id
  - duplicate procedure_ids
  - asset not found
  - unknown service_frequency
  - frequency does not match tag

The blank fields were assessed in the same way as the asset loader; invalid procedure tags were found by comparing again to a list of valid tags; procedure_ids were checked against asset_ids by comparing them to the asset_id plus the procedure tag; duplicate procedure_ids were also assessed in the same way as the asset loader. Asset not found checks were done by comparing asset_ids to the outputs that passed the asset loader checks, so a procedure for an asset that failed the asset loader checks also fails; unknown service_frequency was checked by comparing to the frequency loader output, and expected tag interval was compared to the frequency loader interval output. 

I initially defined the valid tags as `VALID_SLOT` at the top of the function but replaced it with a line defining the expected tag intervals in `SLOT_DAYS` so that the line could serve two purposes by providing the valid tags in the form of the dictionary keys and the expected tag intervals as the values, so both checks use one line of given information.

The sample output is as follows: `8 good rows
7 rejected rows
10 invalid procedure tag
11 procedure_id does not match asset_id
12 asset not found
13 unknown service_frequency
14 frequency does not match tag
15 duplicate procedure_id
16 blank description`

This was the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/03-load-procedures.ipynb) used.

The `load_procedures()` function was moved to the [loaders](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) file, alongside the other loader functions, and, again, the final clean and rejected rows were appended to the respective lists, and the function returns those values. The argument of this function, unlike the others is not just `path`, it is `path, valid_asset_ids, frequencies` where `valid_asset_ids` is the output of the asset loader, and `frequencies` is the output of the frequency loader, since the function used both of those.

After that was the final loader for the `service_history.csv`. Again, following the framework of the previous loaders, the failure criteria for these rows were:
  - blank fields
  - invalid date_completed
  - duplicate record_ids
  - procedure not found
  - future date_completed
  - date_completed before commissioning

Again, the blank fields were assessed in the same way as the other loaders; a block was used to convert the date_completed string into a datetime object in the appropriate `DATE_FMT`; just like with commissioning_date in the assets loader, if date_completed is in an invalid format, this would return a `ValueError` and then identify the row as bad; duplicate record_ids were also assessed in the same way as the other loaders. Procedure not found checks were done in the same manner as the asset not found check in the previous loader; and the future date_completed and date_completed before commissioning checks were done by comparing those datetime values to the assigned datetime values for `today` and `commissioning_date`.

The order of the checks mattered here: date_completed had to parse into a valid datetime first, the value is kept as `done` for future use, and the procedure had to be verified before its commissioning date could be looked up.

I decided to include a set datetime parameter for `today` (2026-10-21) for testing purposes; this will be changed later in the process to have a live `today` value.

Similar to the `SLOT_DAYS` in the last loader, I initially defined the procedure_ids for the procedure_id check but replaced it with a procedure_commissioning dictionary that could again serve two purposes: the keys give the procedure_ids for that check, and the values give the commissioning_dates.

As with the `linked_asset_id` column in the assets table, the notes column in the service history table is also an 'optional' column. For these, if blank, they are assigned a `None` value, since it is valid for them to be blank, unlike all other required columns.

In the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/04-load-service-history.ipynb), to ensure all the required data was fed to the function, I had to chain the loaders together; frequencies and valid assets feed the procedures loader; the procedures plus asset commissioning dates are combined into procedure_commissioning, which feeds the service history loader.

The sample output is as follows: `10 good rows
6 rejected rows
12 procedure not found
13 invalid date_completed
14 future date_completed
15 duplicate record_id
16 date_completed before commissioning
17 blank date_completed`

Some issues I ran into with this stage: I once again accidentally put my accept lines into the loop, resulting in inflated row numbers. I messed up on using `strptime` by attempting to write a `datetime.strptime()` line and then calling it in a subsequent line. I switched in this phase from building in notebooks and copy-pasting over to the [loader](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) file because I wanted to avoid possible indentation errors, which are difficult to debug when copy-pasting, but navigating this switch came with some hitches as I ran into `NameError`s and had to learn that everything has to be defined or imported before testing from outside the notebook since each notebook has its own memory, so the ease of testing is traded off for avoiding tedious indentation debugging, which I think is worth it because the testing by saving the file and restarting the kernel is still less of a hassle than manually rechecking every line indent.

At this point, all the loaders are complete, finally :), and the only things left for this phase are to write the generator scripts and loader tests, which I will come back to after starting the database work because I need a bit of a break, and I really enjoy databases, so it will be a nice change of pace.

*2026-10-25: At this point, when I had a moment to mentally regroup, I made some design decisions for the process going forward. My original plan was to write a generator script based on the initial .csv files to create larger asset datasets, then use a SQLite database to store and organize the data and also for querying, and then use `matplotlib` in Python to create the reports. I have now decided to scale back the matplotlib element to possibly one chart and shift the rest of the reporting phase to Excel instead, so I can have some solid Excel experience in my portfolio, since for data analytics Excel comes up way more frequently than matplotlib. All other elements will remain the same. I'll decide the specifics when we come back to this at a later point.

Starting the SQLite phase, I created a Frequencies table using `DROP TABLE IF EXISTS` so reruns are safe, defining service_frequency as `TEXT PRIMARY KEY` and service_interval_days as `INTEGER NOT NULL`. The rows were pulled from `load_frequencies` using `executemany` and `?` placeholders. 

Initially, I had a mistaken `AUTOINCREMENT` for service_frequency, which would cause an error since it's not an integer value. Also, I did not have service_interval_days as `NOT NULL`. 

After fixing them, I ran two test lines trying to add a duplicate 'weekly' row and a 'daily' row with a `None` service_interval_days to test the `UNIQUE` and `NOT NULL` constraints. The output of those tests was: `UNIQUE constraint failed: Frequencies.service_frequency
NOT NULL constraint failed: Frequencies.service_interval_days`

This schema is a second line of defense behind the loaders, which already reject bad rows with clear reasons.

The database is in the automatically created `frequencies.sqlite` file, which remains uncommitted since I added a `*.sqlite` line to the `.gitignore`

This is the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/05-sqlite-frequencies.ipynb) used.

The Assets SQLite table was next after that. Following the same framework, rows were loaded from `load_assets`; the table was created using `DROP TABLE IF EXISTS`, defining asset_id as `TEXT PRIMARY KEY` and the others as `TEXT NOT NULL`, with the exception of linked_asset_ids, which is allowed to be `NULL`, so it was just defined as `TEXT`. The status column also got some check constraints, `CHECK (status IN ('active', 'under repair', 'decommissioned'))`, to serve as a second line of defense for the loaders again, ensuring only valid statuses are appended to the database table. 

Foreign keys were turned on for each connection since SQLite automatically ignores them otherwise: `PRAGMA foreign_keys = ON`. Because it was now enforcing foreign keys, this resulted in a circular error link due to assets `MTR-001` and `PMP-001` pointing at each other, so whichever row is added first would point to a row that does not yet exist, giving `FOREIGN KEY constraint failed`. This error proves that it was checking for foreign keys. The rows were added using `cur.execute` and `?` placeholders, just as with the previous table.

I had some mess-ups here, like not putting the appropriate commas at the end of the lines defining each column in the `DROP TABLE` BLOCK, accidentally not including the location column of the table, and writing the loop the same way as for the previous table, which treated the loader output as a dictionary instead of lists. I also got a `database is locked` issue when trying to run the code again after the foreign key error because I forgot to restart the kernel.

To fix the foreign key error, I assigned the linked_asset_id values as `None` then added a block before the commit to `UPDATE` the rows and assign all the values once all the rows exist, so it never points to a row that hasn't been added yet. This is similar to the asset loader working in two passes also to accommodate the linked_asset_id linking to other rows.

Then I added the test cell to attempt adding an invalid status to fail the status check and updating an asset_id to one that did not exist to once again fail the foreign key constraint to prove that the checks were functioning. The output of these checks was: `CHECK constraint failed: status IN ('active', 'under repair', 'decommissioned')
FOREIGN KEY constraint failed.`

The database file here is also covered by .gitignore, so it remains uncommitted.

This is the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/06-sqlite-assets.ipynb) used for this.
