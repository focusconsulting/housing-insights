var allDataObjects = [];

function DataObject(tableName, queryModifiers){
  allDataObjects.push(this);
  // fetches data from the API unless already loaded.
  // 'tableName' is a string taken from meta.json.
  // queryModifiers is an object litera. These wouldn't
  // be SQL queries but rather options for the API call. E.g. the constructor call
  // be, 'new DataObject('project', { 'zone' : 'ward' }

  // We still need to work out how to represent the process of grabbing data
  // from other data objects. This could be a method ('getFrom(dataObject)', or
  // it could be a property of the queryModifiers object. We could have the constructor
  // look for any necessary data within existing dataObjects first.)

  this.data; //returns the data

}

  // The assumption is that we'll create DataObject instances within the view-specific
  // .js files.