# transform the the new TOPA dataset provided by CNHED
# into the same shape that the existing RSCAD TOPA dataset is

from sqlalchemy import create_engine, text
import pandas as pd
import os

db_engine = create_engine(
    "postgresql://codefordc:codefordc@postgres:5432/housinginsights_docker")
connection = db_engine.connect()


results_dir = os.path.join(os.path.dirname(
    __file__), "../../data/raw/TOPA_notices/20210807/")
df = pd.read_csv(
    '../../data/raw/TOPA_notices/20210807/ahpc_topa_raw.csv', encoding="latin-1")


df.rename(columns={'Address for mapping': 'Address',
                   'Offer of Sale date (usually DHCD receipt date)': 'Notice_date',
                   '# Units': 'Num_units',
                   'Final sale price': 'Sale_price',
                   }, inplace=True)

df['ADDRESS_ID'] = 0
df['Nidc_rcasd_id'] = ''
df['_NOTES_'] = df['Notes']
# Attempt to use existing topa data to fill in missing data
for index, row in df.iterrows():
    clean_address = row['Address'].__str__().replace(',', '')
    clean_address = clean_address.replace('\n', '')
    clean_address = clean_address.replace('\r', '')
    clean_address = clean_address.upper()
    query = text("SELECT * from topa where address_std = :x")
    existing_topa_row = connection.execute(
        query, x=clean_address).fetchall()
    if(len(existing_topa_row) > 0):
      # There is an existing topa entry for this address that can be resused
        db_row = existing_topa_row[0]
        df.at[index, 'ADDRESS_ID'] = db_row['address_id']
        df.at[index, 'Nidc_rcasd_id'] = db_row['nidc_rcasd_id']
    else:
        # No row so we attempt to assign default values
        hashed_address = abs(hash(clean_address)) % (10 ** 6)
        df.at[index, 'ADDRESS_ID'] = hashed_address
        df.at[index, 'Nidc_rcasd_id'] = hashed_address
    # Fix number of unit data
    clean_units = row['Num_units'].__str__().replace('+', '')
    clean_units = clean_units.replace('?', '')
    clean_units = clean_units.replace(' ', '')
    if clean_units == 'nan':
        clean_units = 0
    else:
        clean_units = int(clean_units)
    df.at[index, 'Num_units'] = clean_units

    # Fix notes data
    clean_notes = row['_NOTES_'].__str__()
    clean_notes = clean_notes.replace('\n', '')
    clean_notes = clean_notes.replace('\r', '')
    clean_notes = clean_notes.replace('"', '')
    clean_notes = clean_notes.replace(';', '')

    df.at[index, '_NOTES_'] = clean_notes
    df.at[index, 'Notes'] = clean_notes

    # Fix sale_price
    if isinstance(row['Sale_price'], str):
        clean_price = row['Sale_price'].replace('$', '')
        clean_price = clean_price.replace(',', '')
        df.at[index, 'Sale_price'] = int(float(clean_price))

    # Fix address
    df.at[index, 'Address'] = clean_address

    # Fix Notice_date
    if '?' in row['Notice_date']:
        df.at[index, 'Notice_date'] = '08/07/2021'


# Fix the column types
# df['Sale_price'] = df['Sale_price'].astype(np.int64)

# Add required columns that do not exist in new data
df['X'] = 0
df['Y'] = 0
df['Addr_num'] = ''
df['_SCORE_'] = 0
df['_STATUS_'] = ''
df['_MATCHED_'] = ''
df['M_OBS'] = ''
df['M_ZIP'] = 0
df['M_STATE'] = 'DC'
df['M_CITY'] = 'Washington'
df['VoterPre2012'] = ''
df['SSL'] = ''
df['Psa2012'] = ''
df['Psa2004'] = ''
df['GeoBlk2010'] = ''
df['GeoBg2010'] = ''
df['Geo2010'] = ''
df['Geo2020'] = ''
df['Geo2000'] = ''
df['Cluster_tr2000'] = ''
df['cluster2017'] = ''
df['Anc2012'] = ''
df['Anc2002'] = ''
df['Source_file'] = 'ahpc_topa.csv'
df['Notice_type'] = ''


# Reuse existing columns to fill in other missing columns
df['address_std'] = df['Address']
df['M_ADDR'] = df['Address']
df['Orig_address'] = df['Address']
df['Ward2022'] = df['Ward']
df['Ward2012'] = df['Ward']
df['Ward2002'] = df['Ward']


# Drop all unused columns
df.drop(columns=[
    " RCSD Report week ending in date",
    "All street addresses",
    "Property name",
    "Outcome",
    "Subsidy",
    "Offer Price",
    "Offer price per unit",
    "Contract? (Y/N)",
    "Technical assistance provider",
    "Tech. Assist. Staff",
    "Date of Contract",
    "Ward",
    "# Units Occupied",
    "# Units Assn Members",
    "DOPA Notice? Yes / No (Date)",
    "P&S Seller (Owner at time of sale)",
    "P&S Buyer (Contract Purchaser)",
    "P&S Broker (Sellers Agent)",
    "Sellers Mgmt Company",
    "Existing Subsidy (Y/N)",
    "Existing Subsidy Type",
    "Existing AMI restrictions",
    "Existing Rent Control (Y/N)",
    "Tenant Assn Lawyer",
    "Development Consultant",
    "Hardship Petition w/in 5-Years of Sale?",
    "Date of Tenant Assn Incorporation",
    "Did a TA claim TOPA rights? (Y/N)",
    "Date DHCD received TA registration",
    "TA Development Partner",
    "TA P&S Contract Date",
    "Date of TA assignment of rights",
    "Price per unit at final sale",
    "Date of Final Closing ",
    "Final Purchaser",
    "Rental, Coop or Condo?",
    "Post-purchase Management Company",
    "Voluntary Agreement? Y/N (Date)",
    "LIHTC Financing? (Y/N)",
    "HPTF Financing? (Y/N?)",
    "Other Public Funding? (Y/N?)",
    "Non-Profit Funding? (Y/N?)",
    "Private Funding? (Y/N?)",
    "Anti-displacement Option for Tenants (Y/N)"
], inplace=True)


df.to_csv(results_dir + 'ahpc_topa.csv', encoding='latin-1', index=False)

print("done")
