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

The sample output of this is:
```
8 good rows
5 rejected rows
rejected lines:
9
10
11
12
14
```

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

The sample output is as follows: 
```
8 good rows
7 rejected rows
10 invalid procedure tag
11 procedure_id does not match asset_id
12 asset not found
13 unknown service_frequency
14 frequency does not match tag
15 duplicate procedure_id
16 blank description
```

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

The sample output is as follows: 
```
10 good rows
6 rejected rows
12 procedure not found
13 invalid date_completed
14 future date_completed
15 duplicate record_id
16 date_completed before commissioning
17 blank date_completed
```

Some issues I ran into with this stage: I once again accidentally put my accept lines into the loop, resulting in inflated row numbers. I messed up on using `strptime` by attempting to write a `datetime.strptime()` line and then calling it in a subsequent line. I switched in this phase from building in notebooks and copy-pasting over to the [loader](https://github.com/alissamaharaj/due-diligence/blob/main/src/loaders.py) file because I wanted to avoid possible indentation errors, which are difficult to debug when copy-pasting, but navigating this switch came with some hitches as I ran into `NameError`s and had to learn that everything has to be defined or imported before testing from outside the notebook since each notebook has its own memory, so the ease of testing is traded off for avoiding tedious indentation debugging, which I think is worth it because the testing by saving the file and restarting the kernel is still less of a hassle than manually rechecking every line indent.

At this point, all the loaders are complete, finally :), and the only things left for this phase are to write the generator scripts and loader tests, which I will come back to after starting the database work because I need a bit of a break, and I really enjoy databases, so it will be a nice change of pace.

*2026-10-25: At this point, when I had a moment to mentally regroup, I made some design decisions for the process going forward. My original plan was to write a generator script based on the initial .csv files to create larger asset datasets, then use a SQLite database to store and organize the data and also for querying, and then use `matplotlib` in Python to create the reports. I have now decided to scale back the matplotlib element to possibly one chart and shift the rest of the reporting phase to Excel instead, so I can have some solid Excel experience in my portfolio, since for data analytics Excel comes up way more frequently than matplotlib. All other elements will remain the same. I'll decide the specifics when we come back to this at a later point.

Starting the SQLite phase, I created a Frequencies table using `DROP TABLE IF EXISTS` so reruns are safe, defining service_frequency as `TEXT PRIMARY KEY` and service_interval_days as `INTEGER NOT NULL`. The rows were pulled from `load_frequencies` using `executemany` and `?` placeholders. 

Initially, I had a mistaken `AUTOINCREMENT` for service_frequency, which would cause an error since it's not an integer value. Also, I did not have service_interval_days as `NOT NULL`. 

After fixing them, I ran two test lines trying to add a duplicate 'weekly' row and a 'daily' row with a `None` service_interval_days to test the `UNIQUE` and `NOT NULL` constraints. The output of those tests was: 
```
UNIQUE constraint failed: Frequencies.service_frequency
NOT NULL constraint failed: Frequencies.service_interval_days
```

This schema is a second line of defense behind the loaders, which already reject bad rows with clear reasons.

The database is in the automatically created `frequencies.sqlite` file, which remains uncommitted since I added a `*.sqlite` line to the `.gitignore`

This is the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/05-sqlite-frequencies.ipynb) used.

The Assets SQLite table was next after that. Following the same framework, rows were loaded from `load_assets`; the table was created using `DROP TABLE IF EXISTS`, defining asset_id as `TEXT PRIMARY KEY` and the others as `TEXT NOT NULL`, with the exception of linked_asset_ids, which is allowed to be `NULL`, so it was just defined as `TEXT`. The status column also got some check constraints, `CHECK (status IN ('active', 'under repair', 'decommissioned'))`, to serve as a second line of defense for the loaders again, ensuring only valid statuses are appended to the database table. 

Foreign keys were turned on for each connection since SQLite automatically ignores them otherwise: `PRAGMA foreign_keys = ON`. Because it was now enforcing foreign keys, this resulted in a circular error link due to assets `MTR-001` and `PMP-001` pointing at each other, so whichever row is added first would point to a row that does not yet exist, giving `FOREIGN KEY constraint failed`. This error proves that it was checking for foreign keys. The rows were added using `cur.execute` and `?` placeholders, just as with the previous table.

I had some mess-ups here, like not putting the appropriate commas at the end of the lines defining each column in the `DROP TABLE` BLOCK, accidentally not including the location column of the table, and writing the loop the same way as for the previous table, which treated the loader output as a dictionary instead of lists. I also got a `database is locked` issue when trying to run the code again after the foreign key error because I forgot to restart the kernel.

To fix the foreign key error, I assigned the linked_asset_id values as `None`, then added a block before the commit to `UPDATE` the rows and assign all the values once all the rows exist, so it never points to a row that hasn't been added yet. This is similar to the asset loader working in two passes also to accommodate the linked_asset_id linking to other rows.

Then I added the test cell to attempt adding an invalid status to fail the status check and updating an asset_id to one that did not exist to once again fail the foreign key constraint to prove that the checks were functioning. The output of these checks was: 
```
CHECK constraint failed: status IN ('active', 'under repair', 'decommissioned')
FOREIGN KEY constraint failed.
```

The database file here is also covered by .gitignore, so it remains uncommitted.

This is the [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/06-sqlite-assets.ipynb) used for this.

*2026-10-26: Moving forward, I decided to create one big file, [storage.py](https://github.com/alissamaharaj/due-diligence/blob/main/src/storage.py), that connects each data loader to a single database location, instead of having each file create its own database at its location. The file path `DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'maintenance.sqlite'` was defined as the database location. The file also holds the entire database-building script, including building the tables and inserting the data. Creating this file path solves the issue so the scripts work no matter which folder the code is launched from and prevents SQLite from creating new empty databases in the wrong folder if the file path doesn't resolve.

`get_conn()` then connects to `DB_PATH`, activates foreign keys, and returns the connection.
Issues I ran into here were attempting to connect to a bare filename instead of the correct path and forgetting to include the return.

For the .csv path, the already created `DB_PATH` was derived as `DATA_DIR = DB_PATH.parent`.

`create_freq` and `create_assets` were moved from notebooks using `executescript`; `create_proc` and `create_history` were built from scratch directly in the storage file using the existing two as templates. The `DROP TABLE` lines were removed from the individual functions and included in the `build_database()` one instead, since the drop orders rely on how the tables relate to each other, and this function sees all four tables. Drops go children first, and creates go parents first. The hitch for me here was using commas between DROP TABLE lines instead of semicolons.

Then the insert functions for the good rows from each loader were built. `insert_assets` follows the same two-pass approach by inserting all the linked_asset_ids as `None`, then updating them on a second pass. I had some issues with `insert_proc` because of the arguments required for the `load_procedures` function, so I had to define those arguments `(valid_asset_ids, frequencies)` in the setup lines before I could call it. `insert_history` was the same but even more complex and required more setup lines to identify the data the function needed passed into it to run (data from `load_procedures` and `procedure_commissioning, today`, which also meant including datetime values instead of strings). In `insert_history`, the loader notebook still uses the fixed date, so for the loader tests I’ll need to pass a fixed `today` to keep results from changing as the date changes.

The `load_database()` function was built next; it calls `build_database`, runs the insert functions, then commits.

`load_database()` was tested in [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/07-storage-test.ipynb) cells. The final output of counts in each table was: 
```
Frequencies 4
Assets 7
Procedures 8
Service_History 10
```
A second test cell for Assets still showed 7, confirming that the commit reached the file and that running it twice did not cause a double count since the drop cleared the tables.

*2026-10-27: For the [test_loaders.py](https://github.com/alissamaharaj/due-diligence/blob/main/tests/test_loaders.py), I decided to go with `unittest` instead of plain `assert` so that when the test runs, if there are failures, it would identify each individually to make resolving failures easier.

Similar to `storage.py`, the file paths were defined using `ROOT = Path(__file__).resolve().parent.parent`, `SRC_DIR = ROOT / 'src'`, `DATA_DIR = ROOT / 'data'`, and `sys.path.append(str(SRC_DIR))`, so the test always finds `/src` and `/data` no matter what folder it's launched from, which were then imported from the `loaders` file.

This was my first time using OOP for a project, so the class creation was tricky for me at first. When trying to create the first test class, I didn't write it to inherit `unittest.TestCase`, I included an `__init__` that was unnecessary and broke the code, mistakenly included an extra `.parent` in the file path, used a realtive `sys.path`, and placed the loaders import in the wrong place for the defining order, it needed to go after the relative path was defined, but I placed it before. Debugging these issues was a good learning experience for me. Making mistakes is always a better teacher than following a step-by-step procedure.

The test cases first verify that the number of good and rejected lines are as expected, then compare the output to the expected dictionary/lists/strings/etc., as the case might be. An accidental typo in the asserted output reason string proved that the test was working as intended; for the other cases, after the first test ran successfully, I purposefully included typos to show that the test identifies differences in the asserted output and the actual output. The tests use the actual `.csv`s instead of building samples specifically for testing, so in the future, when changes are made to the .csv files, or when the generator script creates the large asset datasets, the version of the files used for the test cases would need to be frozen so as to not break the tests.

Most of the test cases follow the same general format in terms of variable definitions as their respective insert functions from the `storage.py` file, but for `TestServiceHistory` instead of using a live `datetime.now`, a static `today = datetime(2026, 10, 21)` was used so that the test case doesn't break with calendar drift.

After creating all the test cases, since there were multiple shared lines of setup variables between the `TestProcedures` and the `TestServiceHistory` classes, I decided to try out the `setUp` method that is available for classes as an interesting addition to the exercise, as well as simplifying the code. In it, I included the `load_frequencies`, `load_assets`, and `valid_asset_ids` lines, which were shared by the two test cases in the `SharedSetup` class, which inherits `unittest.TestCase`. Then I changed `TestProcedures` and `TestServiceHistory` to inherit `SharedSetup`.

All four test cases run as expected after this process. This was the sample output:
```
....
----------------------------------------------------------------------
Ran 4 tests in 0.007s

OK
```

*2026-10-28: Moving back to create the [generator](https://github.com/alissamaharaj/due-diligence/blob/main/src/generator.py) file. Some design decisions made upfront: the number of assets generated has to be restricted since the procedures and service history have multiple rows per asset, and those tables could become very large depending on the number of assets. I'm thinking of generating around 30-40 assets. Also, for the initial generated rows, I'm doing clean rows only first; then, when I have that down, I'll generate bad rows.

At the top of the file, `csv`, `random`, `datetime/timedelta`, and `Path` were imported. The root path was defined just as in the storage and test files `ROOT = Path(__file__).resolve().parent.parent`, and the future output location path `OUT_DIR = ROOT / 'data' / 'generated'`. Then I defined all the variable fields for the `assets.csv`, including the headers, VALID_TYPEs, type: description pairs, locations, DATE_FMT for commissioning_date, and VALID_STATUSes.

Then the `plan_counts()` function was defined. For a count of assets in the range of 30-40, taking the required pump: motor pairs into consideration, the number of pairs allowed must leave enough counts to include 2 of each other asset type: generator, transformer, boiler, and hvac; therefore, the maximum number of pairs has to be the total number of assets - 8, all divided by 2. This provides the restriction for the maximum number of pairs. After the number of pumps and motors are generated, the spare counts are used for other asset types.

In a `if __name__ == '__main__':` block, `plan_counts()` was called for a random `rng` value, 5 times to test it. the `__name__` block is used so that when the function is imported into another file for use this section is ignored.
```
for seed in range(5):
        counts = plan_counts(random.Random(seed))
        print(seed, counts, sum(counts.values()))
```
The output of this test was:
```
0 {'PMP': 9, 'MTR': 9, 'GEN': 3, 'TRN': 4, 'HVC': 6, 'BLR': 5} 36
1 {'PMP': 10, 'MTR': 10, 'GEN': 4, 'TRN': 2, 'HVC': 3, 'BLR': 3} 32
2 {'PMP': 8, 'MTR': 8, 'GEN': 3, 'TRN': 4, 'HVC': 5, 'BLR': 2} 30
3 {'PMP': 10, 'MTR': 10, 'GEN': 4, 'TRN': 3, 'HVC': 3, 'BLR': 3} 33
4 {'PMP': 9, 'MTR': 9, 'GEN': 6, 'TRN': 3, 'HVC': 2, 'BLR': 4} 33
```
It shows that each run generated a count within the range, always matched the number of pumps and motors, and always had at least 2 of each other asset type.

Next was the `make_asset()` function. Each  variable was defined using the VALID_TYPE prefixes for the `asset_id` and `asset_type`; descriptions and locations are random choices from the defined lists; commissioning_date uses a randomly generated past datetime, relative to the `today` datetime passed into the argument of the function, and the status is assigned as 'active' for every row so far. The function returns a dictionary with each header as the keys and the generated values. `linked_assets` are added directly instead of on a second pass, as it usually is, since the required asset_id pairs exist before the dictionary is built, so there is no error to avoid.

The `__name__` block was changed to now test the `make_asset(rng, today, prefix, number, linked_id='')` function using:
`print(make_asset(random.Random(1), datetime(2026, 10, 28), 'PMP', 1, 'MTR-001'))`.
The output of this test was: `{'asset_id': 'PMP-001', 'type': 'pump', 'description': 'Cooling Water Pump', 'location': 'Rooftop', 'commissioning_date': '2026-05-22', 'status': 'active', 'linked_asset_id': 'MTR-001'}` showing that all the fields are generated as expected.

*2026-10-29: Built the `generate_assets(rng, today)` function using `plan_counts`; string formatting was used to generate pump and motor ids for the range of the counts, and they are then appended to a list. The same is then done for the other asset types, and the list is returned.

The `__name__` block was again used for testing: 
```
assets = generate_assets(random.Random(42), datetime(2026, 10, 28))
print(len(assets))
for a in assets[:4]: print(a)
```
The output of this test was:
```
40
{'asset_id': 'PMP-001', 'type': 'pump', 'description': 'Cooling Water Pump', 'location': 'Substation', 'commissioning_date': '2023-06-10', 'status': 'active', 'linked_asset_id': 'MTR-001'}
{'asset_id': 'MTR-001', 'type': 'motor', 'description': 'Spare Motor', 'location': 'Boiler Room', 'commissioning_date': '2025-11-06', 'status': 'active', 'linked_asset_id': 'PMP-001'}
{'asset_id': 'PMP-002', 'type': 'pump', 'description': 'Standby Feedwater Pump', 'location': 'Generator Room', 'commissioning_date': '2025-03-08', 'status': 'active', 'linked_asset_id': 'MTR-002'}
{'asset_id': 'MTR-002', 'type': 'motor', 'description': 'Mixer Motor', 'location': 'Pump Room 1', 'commissioning_date': '2024-11-08', 'status': 'active', 'linked_asset_id': 'PMP-002'}
```
This shows that the number of assets generated is within the set range, and for the sample printed, all the fields match what is intended per row and type.

Small hitch I had with this stage: I included the append lines outside the intended loop at first, resulting in a number of assets appended to the list that was outside of the intended range.

Then I built the `write_csv(path, rows, fieldnames)`. `path.parent.mkdir(parents=True, exist_ok=True)` is used to open the correct folder from the given path and create the file if it does not already exist. `open()` is used to open the file for writing, and `csv.DictWriter` is used to write rows as a dictionary.
A final `__name__` block was used for testing. A live datetime was used for testing even though a static datetime was used for building, since the final version will use a live datetime.
```
    assets = generate_assets(random.Random(42), datetime.now())
    write_csv(OUT_DIR / 'assets.csv', assets, fields)
    print(f'wrote {len(assets)} rows')
```
This test successfully created the generated `assets.csv` with 40 rows of assets.

A [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/08-generated-assets-test.ipynb) was used to test the generated assets in the loader. The output of this test was:
```
40 good rows
0 rejected rows
```
as expected.

Then the same was done for `generate_procedures(assets)` as with `generate_assets`. The procedure constants were defined, the generated assets were looped through, and used as the template to determine what procedures need to be generated per asset. For each procedure tag per asset, a `procedure_id`, `asset_id`, `description`, and `service_frequency` are returned as a dictionary where these fields are the keys.

One hitch I encountered here: I accidentally built the function to append key: value pairs at first instead of dictionaries per row.

The `__name__` block test was performed: 
```
assets = generate_assets(random.Random(42), datetime.now())
    write_csv(OUT_DIR / 'assets.csv', assets, fields)
    print(f'wrote {len(assets)} rows')
    procedures = generate_procedures(assets)
    write_csv(OUT_DIR / 'procedures.csv', procedures, proc_fields)
    print(f'wrote {len(procedures)} procedure rows')
```
and the `procedures.csv` was successfully generated with 160 rows.

A similar [notebook](https://github.com/alissamaharaj/due-diligence/blob/main/notebooks/09-generated-procedures-test.ipynb) test to the one performed for the `generate_assets` function was performed. This was the output of that test:
```
160 good rows
0 rejected rows
```
as expected.
