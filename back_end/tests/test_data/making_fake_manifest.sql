CREATE TABLE manifest(
    include_flag TEXT,
    destination_table TEXT, 
    unique_data_id TEXT,
    data_date TEXT,
    local_folder TEXT,
    s3_folder TEXT,
    filepath TEXT,
    notes TEXT,
    PRIMARY KEY (unique_data_id);



INSERT INTO manifest (
    include_flag,
    destination_table, 
    unique_data_id,
    data_date,
    local_folder,
    s3_folder,
    filepath,
    notes)
VALUES ('loaded', 'buildings', 'my_data_id', '2001', '/data', '/data', 'path.csv', '');

SELECT * FROM manifest;