'use strict';

var filterView = {
  init: function (msg, data) {
    //msg and data are from the pubsub module that this init is subscribed to.
    //when called from dataLoaded.metaData, 'data' is boolean of whether data load was successful

    if (data === true) {
      //Make sure other functionality is hooked up
      setSubs([
        ['filterViewLoaded', filterUtil.init],

        ['sidebar', filterView.toggleSidebar],
        ['dataLoaded.filterData', filterView.setUpAssetToggler],
        ['subNav', filterView.toggleSubNavButtons],
        ['filterValues', filterView.indicateActivatedFilters],
        ['anyFilterActive', filterView.handleFilterClearance],
        ['filterValues', filterView.addClearPillboxes],
        ['dataLoaded.filterData', filterView.formatFilterDates],
        ['filterDatesFormatted', filterView.buildFilterComponents],
        ['subNavExpanded.right', filterView.expandSidebar],
        ['mapLayer', filterView.clearLocationBasedFilters],
        ['mapLayer', filterView.updateLocationFilterControl],
        ['mapLayer', filterView.resetZoneFilters],
        ['filterViewLoaded', filterView.updateLocationFilterControl], //handles situation where initial mapLayer state is triggered before the dropdown is available to be selected
        //['anyFilterActive', filterView.clearAllInvalid]
      ]);

      setState('subNav.left', 'layers');
      setState('subNav.right', 'buildings');

      //TODO this is for the triangular boxes to expand/collapse, which might be tweaked in new UI. Check if this is still relevant.
      document.querySelectorAll('.sidebar-tab').forEach(function (tab) {
        tab.onclick = function (e) {
          var sideBarMsg = e.currentTarget.parentElement.id.replace('-', '.');
          filterView.toggleSidebarState(sideBarMsg);
        };
      });

      //Expand/Collapse right sidebar control clickbacks
      d3.select('#expand-sidebar-right').on('click', function () {
        //toggle which control is shown
        d3.selectAll('#sidebar-control-right i').classed('hidden', true);
        d3.select('#compress-sidebar-right').classed('hidden', false);

        setState('subNavExpanded.right', true);
      });

      d3.select('#compress-sidebar-right').on('click', function () {
        //Toggle which control is shown
        d3.selectAll('#sidebar-control-right i').classed('hidden', true);
        d3.select('#expand-sidebar-right').classed('hidden', false);

        setState('subNavExpanded.right', false);
      });

      document.querySelectorAll('.sub-nav-button').forEach(function (button) {
        button.onclick = function (e) {
          var leftRight = e.currentTarget.parentElement.id.replace(
            '-options',
            ''
          );
          var subNavType = e.currentTarget.id.replace('button-', '');
          if (
            getState()['sidebar.' + leftRight] &&
            getState()['sidebar.' + leftRight][0]
          ) {
            // if the associated sidebar is open
            if (getState()['subNav.' + leftRight][0] === subNavType) {
              // if the clicked subNav button is already active
              setState('sidebar.' + leftRight, false); // close the sidebar
            }
          } else {
            setState('sidebar.' + leftRight, true); // open the sidebar
          }
          setState('subNav.' + leftRight, subNavType);
        };
      });

      //Get the data and use it to dynamically apply configuration such as the list of categorical options
      controller.getData({
        name: 'filterData',
        url: model.URLS.filterData,
      });
    } else {
      console.log('ERROR data loaded === false');
    }

    // For inheritance
    filterView.continuousFilterControl.prototype = Object.create(
      filterView.filterControl.prototype
    );
    filterView.categoricalFilterControl.prototype = Object.create(
      filterView.filterControl.prototype
    );
    filterView.locationFilterControl.prototype = Object.create(
      filterView.categoricalFilterControl.prototype
    );
  }, //end init
  // Iterate through dataCollection.filterData and, for any property
  // that's of type 'date', turn the value into a JS date.
  // This is necessary for comparing dates.
  formatFilterDates: function () {
    var dateComponents = filterView.components.filter(function (component) {
      return component.component_type === 'date';
    });

    // assumes the string is of the format yyyy-mm-dd.
    function makeDateFromString(val) {
      if (val === null) {
        return null;
      }
      var dateSplit = val.split('-');

      return new Date(+dateSplit[0], +dateSplit[1] - 1, +dateSplit[2]);
    }

    model.dataCollection.filterData.objects.forEach(function (item) {
      dateComponents.forEach(function (dateComponent) {
        if (item.hasOwnProperty(dateComponent.source)) {
          item[dateComponent.source] = makeDateFromString(
            item[dateComponent.source]
          );
        }
      });
    });

    setState('filterDatesFormatted', true);
  },
  filterControls: [],
  filterControlsDict: {},
  filterControl: function (component) {
    //TODO refactor to use Dict instead of list version. Keeping both for now
    filterView.filterControls.push(this);
    filterView.filterControlsDict[component.short_name] = this;
    this.component = component;
  },
  nullValuesToggle: function (component, filterControl) {
    //component: the configuration data from dataChoice.js
    //filterControl: the parent control object

    //Alias
    var ths = this;

    //Add the element and set to default value
    this.container = document.createElement('div');
    this.container.classList.add('nullsToggleContainer');

    //Add the tooltip on hover
    var tooltipText =
      'Some projects might be missing data for this field. Check this box to include projects with missing data in the map view.';
    this.container.setAttribute('data-toggle', 'tooltip');
    this.container.setAttribute('data-placement', 'top');
    this.container.setAttribute('title', tooltipText);
    $(this.container).tooltip();

    this.element = document.createElement('input');
    this.element.setAttribute('type', 'checkbox');
    this.element.setAttribute('value', 'showNulls-' + component.source);
    this.element.setAttribute('name', 'showNulls-' + component.source);
    this.element.checked = true;

    var txt = document.createTextNode(
      'Include projects with missing ' + component.display_name + ' data'
    );

    this.toDOM = function (parentElement) {
      parentElement.appendChild(this.container);
      this.container.appendChild(this.element);
      this.container.appendChild(txt);
    };
  },
  filterInputs: {}, // adding filterInputs object so we can access them later -JO //TODO should switch to filterControls instead -NH
  dateInputs: {}, // same for date inputs - JO //TODO same -NH

  // filterTextInput takes as a parameter an array of keys.
  // It produces text inputs corresponding to these keys and
  // tracks their values.
  // sourceObj is one element in dataChoices.
  // keyValuePairsArray takes the form, [[key, val], [key, val]...]
  filterTextInput: function (
    sourceObj,
    keyValuePairsArrayMin,
    keyValuePairsArrayMax
  ) {
    var output = {
      min: {},
      max: {},
    };

    var initialValues = {
      min: keyValuePairsArrayMin,
      max: keyValuePairsArrayMax,
    };

    var submitButton = document.createElement('button');
    submitButton.classList.add('nullValuesToggleSubmit');
    submitButton.setAttribute('type', 'button');

    //function that creates the text boxes on the page
    this.toDOM = function (parentElement, separatorCallback) {
      // separatorCallback is a function that returns
      // a JavaScript Node object to be appended after each
      // input element.

      var toSpan = document.createElement('span');
      toSpan.textContent = 'to';
      for (var pole in output) {
        for (var key in output[pole]) {
          parentElement.appendChild(output[pole][key]);
          if (
            separatorCallback &&
            Object.keys(output[pole]).indexOf(key) <
              Object.keys(output[pole]).length - 1
          ) {
            parentElement.appendChild(separatorCallback());
          }
        }
        if (pole === 'min') {
          parentElement.appendChild(toSpan);
        }
      }
      parentElement.appendChild(submitButton);
    };

    this.setValues = function (keyValuePairsArrayMin, keyValuePairsArrayMax) {
      for (var i = 0; i < keyValuePairsArrayMin.length; i++) {
        output.min[keyValuePairsArrayMin[i][0]].value =
          keyValuePairsArrayMin[i][1];
      }
      for (var i = 0; i < keyValuePairsArrayMax.length; i++) {
        output.max[keyValuePairsArrayMax[i][0]].value =
          keyValuePairsArrayMax[i][1];
      }
    };

    this.reset = function () {
      this.setValues(initialValues.min, initialValues.max);
    };

    this.returnValues = function () {
      var valueOutput = {
        min: {},
        max: {},
      };
      for (var pole in valueOutput) {
        for (var key in output[pole]) {
          valueOutput[pole][key] = output[pole][key].value;
        }
      }
      return valueOutput;
    };

    this.setInputCallback = function (callback) {
      this.callback = callback; // making callback function a property of the filterTextInput so we can access it later -JO
      var checkKeyPress = function (e) {
        if (e.charCode === 9 || e.charCode === 13) {
          callback();
        }
      };

      submitButton.addEventListener('click', callback);

      var setUpInputEventListeners = function (element) {
        function setUpKeyPressListener(e) {
          element.addEventListener('keypress', checkKeyPress);
        }

        function tearDownKeyPressListener(e) {
          element.removeEventListener('keypress', checkKeyPress);
        }

        element.addEventListener('focus', setUpKeyPressListener);
        element.addEventListener('blur', function (e) {
          callback();
          tearDownKeyPressListener(e);
        });
      };
      for (var pole in output) {
        for (var key in output[pole]) {
          setUpInputEventListeners(output[pole][key]);
        }
      }
    };

    this.allInputElements = function () {
      var minInputs = Object.keys(output['min']).map(function (key) {
        return output['min'][key];
      });

      var maxInputs = Object.keys(output['max']).map(function (key) {
        return output['max'][key];
      });
      return minInputs.concat(maxInputs);
    };

    //Create the element and put it
    for (var i = 0; i < keyValuePairsArrayMin.length; i++) {
      output['min'][keyValuePairsArrayMin[i][0]] = document.createElement(
        'input'
      );
      output['min'][keyValuePairsArrayMin[i][0]].setAttribute(
        'id',
        sourceObj.source + '-' + keyValuePairsArrayMin[i][0] + '-text'
      );
      output['min'][keyValuePairsArrayMin[i][0]].classList.add('filter-text');
      output['min'][keyValuePairsArrayMin[i][0]].classList.add(
        keyValuePairsArrayMin[i][0] + '-text'
      );
      output['min'][keyValuePairsArrayMin[i][0]].setAttribute(
        'name',
        keyValuePairsArrayMin[i][0]
      );
      output['min'][keyValuePairsArrayMin[i][0]].value =
        keyValuePairsArrayMin[i][1];
    }
    for (var i = 0; i < keyValuePairsArrayMax.length; i++) {
      output['max'][keyValuePairsArrayMax[i][0]] = document.createElement(
        'input'
      );
      output['max'][keyValuePairsArrayMax[i][0]].setAttribute(
        'id',
        sourceObj.source + '-' + keyValuePairsArrayMax[i][0] + '-text'
      );
      output['max'][keyValuePairsArrayMax[i][0]].classList.add('filter-text');
      output['max'][keyValuePairsArrayMax[i][0]].classList.add(
        keyValuePairsArrayMax[i][0] + '-text'
      );
      output['max'][keyValuePairsArrayMax[i][0]].setAttribute(
        'name',
        keyValuePairsArrayMax[i][0]
      );
      output['max'][keyValuePairsArrayMax[i][0]].value =
        keyValuePairsArrayMax[i][1];
    }
  },
  continuousFilterControl: function (component) {
    //Creates a new filterControl on the sidebar.
    //component is the variable of configuration settings pulled from dataChoices.js

    //Aliases
    var c = component;
    var ths = this;

    //Setup
    filterView.filterControl.call(this, component);
    var contentContainer = filterView.setupFilter(c);

    //Find initial values for controls
    this.calculateParams = function () {
      //Uses the current data set to define min/max levels for the UI.
      //Can be re-run to find new values if the zone type is changed

      //If it's a zone-level data set, need to choose the right column
      var modifier =
        c.data_level == 'zone' ? '_' + getState()['mapLayer'][0] : '';
      var data_field = c.source + modifier;

      var allDataValuesForThisSource = model.dataCollection.filterData.objects.map(
        function (item) {
          return item[data_field];
        }
      );
      ths.minDatum = d3.min(allDataValuesForThisSource) || 0;
      ths.maxDatum = d3.max(allDataValuesForThisSource) || 1;
      ths.datumRange = ths.maxDatum - ths.minDatum;

      function orderOfMagnitude(n) {
        var order = Math.floor(Math.log(n) / Math.LN10 + 0.000000001); // because float math sucks like that
        return Math.pow(10, order);
      }

      ths.orderOfMagnitude = orderOfMagnitude(ths.datumRange);
      ths.stepSize = ths.orderOfMagnitude / 10;
      ths.firstRoundedStep =
        Math.ceil(ths.minDatum / ths.orderOfMagnitude) * ths.orderOfMagnitude;

      if (c.style === 'percent') {
        ths.minDatum = Math.floor(ths.minDatum * 100) / 100;
        ths.maxDatum = Math.ceil(ths.maxDatum * 100) / 100;
      } else {
        //"number", "money"
        ths.minDatum = Math.floor(ths.minDatum);
        ths.maxDatum = Math.ceil(ths.maxDatum);
      }
    };

    this.calculateParams(); //initialize minDatum and maxDatum (based on current zone if applicable)

    //Make the slider itself
    contentContainer
      .append('div')
      .classed('filter', true)
      .classed('slider', true)
      .attr('id', c.source);

    this.slider = document.getElementById(c.source);

    noUiSlider.create(this.slider, {
      start: [this.minDatum, this.maxDatum],
      connect: true,
      range: {
        min: [ths.minDatum],
        '5%': [ths.firstRoundedStep, ths.stepSize],
        max: [ths.maxDatum],
      },
    });

    ////////////////////////
    //Set up the text boxes
    ////////////////////////

    //Create object instance
    this.textBoxes = new filterView.filterTextInput(
      c,
      [['min', this.minDatum]],
      [['max', this.maxDatum]]
    );
    filterView.filterInputs[this.component.short_name] = this.textBoxes; //TODO remove this once we refactor out filterInputs

    //Append a 'span' that will hold the text input boxes
    var inputContainer = document.createElement('span');
    inputContainer.setAttribute('id', c.source + '-input');
    inputContainer.classList.add('text-input', 'continuous');
    document
      .getElementById('filter-content-' + c.source)
      .appendChild(inputContainer);

    //Add it to the DOM
    this.textBoxes.toDOM(
      document.getElementById(c.source + '-input') //parent dom object
    );
    this.textBoxes.allInputElements().forEach(function (el) {
      el.classList.add('continuous-input-text');
    });

    ////////////////////////
    //Set up nulls toggle
    ////////////////////////
    //Set up the toggle button for nulls
    this.toggle = new filterView.nullValuesToggle(c, ths);
    this.toggle.toDOM(document.getElementById('filter-content-' + c.source));

    ////////////////////////
    //Link UI components to state and each other
    ////////////////////////

    //Toggle
    this.toggle.element.addEventListener('change', function () {
      var specificCode = 'filterValues.' + component.source;
      var checkboxValue = ths.toggle.element.checked;
      var textboxValues = ths.textBoxes.returnValues();
      var newState = [
        textboxValues['min']['min'],
        textboxValues['max']['max'],
        checkboxValue,
      ];
      setState(specificCode, newState);
      ths.checkAgainstOriginalValues(
        +textboxValues['min']['min'],
        +textboxValues['max']['max'],
        checkboxValue
      );
    });

    //Textbox
    var inputCallback = function () {
      //When textbox inputs change - need to adjust the slider and setState.
      var specific_state_code = 'filterValues.' + component.source;
      var returnVals = ths.textBoxes.returnValues();
      var minVals = returnVals.min;
      var maxVals = returnVals.max;
      var validateResults = filterView.validateTextInput(
        minVals,
        maxVals,
        component.source,
        component.component_type,
        ths.minDatum,
        ths.maxDatum
      );
      if (validateResults[0]) {
        var setMin = validateResults[1] ? ths.minDatum : minVals.min;
        var setMax = validateResults[2] ? ths.maxDatum : maxVals.max;
        ths.slider.noUiSlider.set([setMin, setMax]);
        ths.textBoxes.setValues([['min', setMin]], [['max', setMax]]); // bind the values in the text boxes to the values
        // potentially just coerced to actual min and actual max
        ths.uncheckNullToggleOnInitialFilterSet();
        setState(specific_state_code, [
          setMin,
          setMax,
          ths.toggle.element.checked,
        ]);
        ths.checkAgainstOriginalValues(
          +setMin,
          +setMax,
          ths.toggle.element.checked
        );
      }
    };
    this.textBoxes.setInputCallback(inputCallback);

    //slider
    function makeSliderCallback(component, doesItSetState) {
      //Make a copy of the callback with access to current variables

      return function sliderCallback(
        values,
        handle,
        unencoded,
        tap,
        positions
      ) {
        /*  This is the custom binding module used by the noUiSlider.on() callback.
                    values: Current slider values;
                    handle: Handle that caused the event;
                    unencoded: Slider values without formatting;
                    tap: Event was caused by the user tapping the slider (boolean);
                    positions: Left offset of the handles in relation to the slider
                */

        //Deal with floating values
        unencoded = unencoded.map(function (el) {
          return el >= 1 ? Math.round(el) : Math.round(el * 100) / 100;
        });

        //Bind the slider values to the textboxes
        var min = unencoded[0];
        var max = unencoded[1];
        ths.textBoxes.setValues([['min', min]], [['max', max]]);
        ths.uncheckNullToggleOnInitialFilterSet();

        //Set the filterValues state
        if (doesItSetState) {
          var specific_state_code = 'filterValues.' + component.source;
          unencoded.push(ths.toggle.element.checked);
          setState(specific_state_code, unencoded);
          ths.checkAgainstOriginalValues(min, max, unencoded[2]);
        }
      };
    }
    this.checkAgainstOriginalValues = function (min, max, showNulls) {
      if (
        min === this.minDatum &&
        max === this.maxDatum &&
        showNulls === true
      ) {
        ths.clear();
      }
    };

    this.uncheckNullToggleOnInitialFilterSet = function () {
      var filterValues = filterUtil.getFilterValues();

      if (
        !filterValues[component.source] ||
        filterValues[component.source].length <= 1 ||
        filterValues[component.source][0].length == 0
      ) {
        console.log('Unchecking the null toggle for ', component.source);
        ths.toggle.element.checked = false;
      }
    };

    // Changing value should trigger map update
    var currentSliderCallback = makeSliderCallback(c, true);
    this.slider.noUiSlider.on('change', currentSliderCallback);

    // Sliding slider should update textboxes only
    var slideSliderCallback = makeSliderCallback(c, false);
    this.slider.noUiSlider.on('slide', slideSliderCallback);

    //Public methods
    this.clear = function () {
      var specific_state_code = 'filterValues.' + component.source;

      ths.slider.noUiSlider.set([ths.minDatum, ths.maxDatum]);
      ths.textBoxes.setValues([['min', ths.minDatum]], [['max', ths.maxDatum]]);
      ths.toggle.element.checked = true;
      setState(specific_state_code, []);
    };

    this.isTouched = function () {
      var returnVals = ths.textBoxes.returnValues();
      return (
        returnVals.min.min != this.minDatum ||
        returnVals.max.max != this.maxDatum ||
        ths.toggle.element.checked === false
      );
    };

    this.set = function (min, max, nullValue) {
      ths.textBoxes.setValues([['min', min]], [['max', max]]);
      ths.slider.noUiSlider.set([min, max]);
      ths.toggle.element.checked = nullValue;

      setState('filterValues.' + c.source, [min, max, nullValue]);
    };

    this.rebuild = function () {
      ths.calculateParams();
      ths.toggle.element.checked = true;
      ths.slider.noUiSlider.updateOptions({
        start: [ths.minDatum, ths.maxDatum],
        range: {
          min: [ths.minDatum],
          '5%': [ths.firstRoundedStep, ths.stepSize],
          max: [ths.maxDatum],
        },
      });
      ths.clear(); //also refills textboxes
    };
  },
  validateTextInput: function (
    minVals,
    maxVals,
    componentSource,
    filterType,
    minDatum,
    maxDatum
  ) {
    var isNaNCount = 0;
    var outOfRangeCount = 0;
    var forceMin = false;
    var forceMax = false; // these will return true if the textInput attempts to set a value beyond the bounds
    // of the actual data
    var invalidEntries = [];

    var doesValidate =
      confirmIsANumber([minVals, maxVals]) &&
      confirmInRange([minVals, maxVals]);

    if (doesValidate) {
      filterView.removeErrors(componentSource);
    } else {
      filterView.showErrors(componentSource, invalidEntries, filterType);
    }
    return [doesValidate, forceMin, forceMax];

    function confirmIsANumber(minAndMax) {
      minAndMax.forEach(function (each, i) {
        for (var key in each) {
          if (each.hasOwnProperty(key)) {
            if (isNaN(+each[key])) {
              isNaNCount++;
              invalidEntries.push([i, key]);
            }
          }
        }
      });

      return isNaNCount === 0 ? true : false;
    }

    function confirmInRange(minAndMax) {
      if (filterType === 'date') {
        minAndMax.forEach(function (each, i) {
          if (+each.month < 1 || +each.month > 12) {
            invalidEntries.push([i, 'month']);
            outOfRangeCount++;
          }
          if (+each.year < 1000 || +each.year > 9999) {
            // just ensuring it's a four-digit number
            invalidEntries.push([i, 'year']); // input that is beyond the range of the actual data
            outOfRangeCount++; // will be coerced to the actual min or actual max below
          }
          var leapYear = +each.year % 4 === 0 ? true : false;
          var maxDay;
          if (+each.month === 2) {
            maxDay = leapYear ? 29 : 28;
          } else if (
            +each.month === 4 ||
            +each.month === 6 ||
            +each.month === 9 ||
            +each.month === 11
          ) {
            maxDay = 30;
          } else {
            maxDay = 31;
          }
          if (+each.day < 0 || +each.day > maxDay) {
            invalidEntries.push([i, 'day']);
            outOfRangeCount++;
          }
        });
        if (
          new Date(
            minAndMax[0].year,
            minAndMax[0].month - 1,
            minAndMax[0].day
          ) >
          new Date(minAndMax[1].year, minAndMax[1].month - 1, minAndMax[1].day)
        ) {
          // ie if input start date is later than the input end date
          invalidEntries.push([0, 'year']);
          invalidEntries.push([1, 'year']);
          outOfRangeCount++;
        }
        if (
          new Date(
            minAndMax[0].year,
            minAndMax[0].month - 1,
            minAndMax[0].day
          ) < minDatum
        ) {
          // coercing here if input min < actual min
          forceMin = true;
        }
        if (
          new Date(
            minAndMax[1].year,
            minAndMax[1].month - 1,
            minAndMax[1].day
          ) > maxDatum
        ) {
          forceMax = true;
        }
      } else {
        console.log('BHDJAK', minAndMax);
        if (minAndMax[0].min > minAndMax[1].max) {
          invalidEntries.push([0, 'min']);
          invalidEntries.push([1, 'max']);
          outOfRangeCount++;
        }
        if (minAndMax[0].min < minDatum) {
          forceMin = true;
        }
        if (minAndMax[1].max > maxDatum) {
          forceMax = true;
        }
      }
      return outOfRangeCount === 0 ? true : false;
    }
  },
  dateFilterControl: function (component) {
    //Creates a new filterControl on the sidebar.
    //component is the variable of configuration settings pulled from dataChoices.js

    //TODO Most of this code is duplicative to the continuousFilterControl. The continuous
    //control has also been refactored while this one hasn't.

    //Should hoist the logic up a level so that the two types can share code.

    filterView.filterControl.call(this, component);
    var c = this.component;
    var ths = this;

    var contentContainer = filterView.setupFilter(c);

    var slider = contentContainer
      .append('div')
      .classed('filter', true)
      .classed('slider', true)
      .attr('id', c.source);

    var inputContainer = document.createElement('span');
    inputContainer.setAttribute('id', c.source + '-input');
    inputContainer.classList.add('text-input', 'date');

    document
      .getElementById('filter-content-' + c.source)
      .appendChild(inputContainer);

    // this is used for d3.min and d3.max.
    var componentValuesOnly = model.dataCollection.filterData.objects.map(
      function (item) {
        return item[c.source];
      }
    );

    var minDatum = d3.min(componentValuesOnly);
    var maxDatum = d3.max(componentValuesOnly);

    slider = document.getElementById(c.source);
    noUiSlider.create(slider, {
      start: [minDatum.getFullYear(), maxDatum.getFullYear()],
      connect: true,
      tooltips: [false, false],
      range: {
        min: minDatum.getFullYear(),
        max: maxDatum.getFullYear(),
      },
      step: 1,
    });
    // as with textInputs, adds each instance of dateInput to the filterView.dateInputs object, so it can be accessed
    // later
    filterView.filterInputs[
      this.component.short_name
    ] = new filterView.filterTextInput(
      component,
      [
        ['month', minDatum.getMonth() + 1],
        ['day', minDatum.getDate()],
        ['year', minDatum.getFullYear()],
      ],
      [
        ['month', maxDatum.getMonth() + 1],
        ['day', maxDatum.getDate()],
        ['year', maxDatum.getFullYear()],
      ]
    );
    var dateInputs = filterView.filterInputs[this.component.short_name];
    function makeSliderCallback(component, doesItSetState) {
      return function sliderCallback(
        values,
        handle,
        unencoded,
        tap,
        positions
      ) {
        // This is the custom binding module used by the noUiSlider.on() callback.

        // values: Current slider values;
        // handle: Handle that caused the event;
        // unencoded: Slider values without formatting;
        // tap: Event was caused by the user tapping the slider (boolean);
        // positions: Left offset of the handles in relation to the slider
        var specific_state_code = 'filterValues.' + component.source;

        var dateForYear = function (minOrMax, year) {
          var minOrMaxObj = {
            min: minDatum,
            max: maxDatum,
          };
          if (year === minOrMaxObj[minOrMax].getFullYear()) {
            return minOrMaxObj[minOrMax];
          } else {
            return new Date(year, 0, 1);
          }
        };

        var newMinDate = dateForYear('min', +unencoded[0]);
        var newMaxDate = dateForYear('max', +unencoded[1]);

        dateInputs.setValues(
          [
            ['year', newMinDate.getFullYear()],
            ['month', newMinDate.getMonth() + 1],
            ['day', newMinDate.getDate()],
          ],
          [
            ['year', newMaxDate.getFullYear()],
            ['month', newMaxDate.getMonth() + 1],
            ['day', newMaxDate.getDate()],
          ]
        );

        ths.uncheckNullToggleOnInitialFilterSet();

        if (doesItSetState) {
          ths.toggle.element.checked;
          setState(specific_state_code, [
            newMinDate,
            newMaxDate,
            ths.toggle.element.checked,
          ]);
          ths.checkAgainstOriginalValues(
            newMinDate,
            newMaxDate,
            ths.toggle.element.checked
          );
        }
      };
    }

    var currentSliderCallback = makeSliderCallback(c, true);
    var slideSliderCallback = makeSliderCallback(c, false);

    // Binding currentSliderCallback to 'change'
    // so that it doesn't trigger when the user changes
    // the filter values through the text input boxes
    // (which then move the slider to a certain position)
    slider.noUiSlider.on('change', currentSliderCallback);

    // Change the value of the text input elements without
    // setting state
    slider.noUiSlider.on('slide', slideSliderCallback);

    function getValuesAsDates() {
      var minVals = dateInputs.returnValues()['min'];
      var maxVals = dateInputs.returnValues()['max'];

      var validateResults = filterView.validateTextInput(
        minVals,
        maxVals,
        component.source,
        component.component_type,
        minDatum,
        maxDatum
      );
      // returns true/false

      var setMin = validateResults[1]
        ? minDatum
        : new Date(minVals.year, minVals.month - 1, minVals.day);
      var setMax = validateResults[2]
        ? maxDatum
        : new Date(maxVals.year, maxVals.month - 1, maxVals.day);

      if (validateResults[0]) {
        dateInputs.setValues(
          // bind the text box values to values potentially coerced to the actual min
          // or max
          [
            ['year', setMin.getFullYear()],
            ['month', setMin.getMonth() + 1],
            ['day', setMin.getDate()],
          ],
          [
            ['year', setMax.getFullYear()],
            ['month', setMax.getMonth() + 1],
            ['day', setMax.getDate()],
          ]
        );
        return {
          min: setMin,
          max: setMax,
        };
      } else {
        return false;
      }
    }

    var inputCallback = function () {
      console.log('in dateFilterControl inputCallback');
      var specific_state_code = 'filterValues.' + component.source;

      var dateValues = getValuesAsDates();
      console.log(dateValues);
      if (dateValues !== false) {
        slider.noUiSlider.set([
          dateValues.min.getFullYear(),
          dateValues.max.getFullYear(),
        ]);

        ths.uncheckNullToggleOnInitialFilterSet();
        setState(specific_state_code, [
          dateValues.min,
          dateValues.max,
          ths.toggle.element.checked,
        ]);
        ths.checkAgainstOriginalValues(
          dateValues.min,
          dateValues.max,
          ths.toggle.element.checked
        );
      }
    };

    // For separating date inputs with a '/'
    function addSlash() {
      return document.createTextNode('/');
    }

    dateInputs.setInputCallback(inputCallback);
    dateInputs.toDOM(document.getElementById(c.source + '-input'), addSlash);

    ////////////////////////
    //Set up nulls toggle
    ////////////////////////
    this.toggle = new filterView.nullValuesToggle(c, ths);
    this.toggle.toDOM(document.getElementById('filter-content-' + c.source));

    //Link toggle action to click
    this.toggle.element.addEventListener('change', function () {
      var specificCode = 'filterValues.' + component.source;
      var checkboxValue = ths.toggle.element.checked;
      var dateValues = getValuesAsDates();
      var newState = [dateValues.min, dateValues.max, checkboxValue];
      setState(specificCode, newState);
      ths.checkAgainstOriginalValues(
        dateValues.min,
        dateValues.max,
        checkboxValue
      );
    });

    this.clear = function () {
      var specific_state_code = 'filterValues.' + component.source;
      // noUISlider native 'reset' method is a wrapper for the valueSet/set method that uses the original options.
      slider.noUiSlider.reset();
      dateInputs.reset();
      ths.toggle.element.checked = true;

      setState(specific_state_code, []);
    };

    this.isTouched = function () {
      var dateValues = getValuesAsDates();
      if (
        document
          .getElementById('filter-' + this.component.source)
          .className.indexOf('invalid') !== -1
      ) {
        return true;
      }
      return (
        dateValues.min.valueOf() !== minDatum.valueOf() ||
        dateValues.max.valueOf() !== maxDatum.valueOf() ||
        ths.toggle.element.checked === false
      );
    };

    this.checkAgainstOriginalValues = function (min, max, showNulls) {
      console.log(min.getTime(), max.getTime(), showNulls);
      console.log(minDatum.getTime(), maxDatum.getTime());
      if (
        min.getTime() === minDatum.getTime() &&
        max.getTime() === maxDatum.getTime() &&
        showNulls === true
      ) {
        console.log('match');
        ths.clear();
      }
    };

    this.uncheckNullToggleOnInitialFilterSet = function () {
      var filterValues = filterUtil.getFilterValues();

      if (
        !filterValues[component.source] ||
        filterValues[component.source].length <= 1 ||
        filterValues[component.source][0].length == 0
      ) {
        console.log('Unchecking the null toggle for ', component.source);
        ths.toggle.element.checked = false;
      }
    };
  },
  showErrors: function (source, invalidEntries, filterType) {
    // eg from dateFilter invalidEntries is array. 1: 0 or 1 (min or max); 2: e.g. 'day'
    // from continuous e.g. [[1,"max"]]
    invalidEntries.forEach(function (each) {
      d3.select('#filter-' + source).classed('invalid', true);
      var invalidInput =
        filterType === 'date'
          ? d3
              .selectAll('#' + source + '-input input.' + each[1] + '-text')
              .nodes()[each[0]]
          : d3
              .select('#' + source + '-input input.' + each[1] + '-text')
              .node();
      console.log(invalidInput);
      invalidInput.classList.add('invalid');
    });
    if (d3.select('#invalid-filter-alert').node() === null) {
      // ie the alert is not already present
      d3.select('#map-wrapper')
        .append('div')
        .attr('id', 'invalid-filter-alert')
        .classed('no-location-alert', true)
        .style('opacity', 0)
        .text('Filter invalid or out of range')
        .transition()
        .duration(1000)
        .style('opacity', 1);
    }
  },
  removeErrors: function (source) {
    d3.select('#filter-' + source).classed('invalid', false);
    d3.selectAll('#' + source + '-input input').classed('invalid', false);
    d3.select('#invalid-filter-alert')
      .transition()
      .duration(1000)
      .style('opacity', 0)
      .remove();
  },
  setupFilter: function (c) {
    //This function does all the stuff needed for each filter regardless of type.
    //It returns the "content" div, which is where the actual UI element for doing
    //filtering needs to be appended

    //Add a div with label and select element
    //Bind user changes to a setState function
    var parent = d3.select('#filter-components');
    var title = parent
      .append('div')
      .classed('title filter-title', true)
      .classed(c.data_level, true);

    //Add data-specific icon
    if (c.data_level == 'project') {
      title
        .append('i')
        .classed('building icon', true)
        .attr('style', 'margin-right:8px;');
    } else if (c.data_level == 'zone') {
      title
        .append('i')
        .classed('icons', true)
        .attr('style', 'margin-right:8px;')
        .html(
          '<i class="home blue icon"></i><i class="corner blue home icon"></i>'
        );
    }

    title.append('span').classed('title-text', true).text(c.display_name);

    title.attr('id', 'filter-' + c.source);

    var content = parent
      .append('div')
      .classed('filter', true)
      .classed(c.component_type, true)
      .classed('content', true)
      .attr('id', 'filter-content-' + c.source);

    var description = content.append('div').classed('description', true);

    //Add data-specific helper text
    if (c.data_level == 'project') {
      var helper = description.append('p').classed('project-flag', true);

      helper.append('i').classed('building icon small', true);

      helper.append('span').html('Project-specific data set');
    } else if (c.data_level == 'zone') {
      var helper = description.append('p').classed('neighborhood-flag', true);

      helper
        .append('i')
        .classed('icons small', true)
        .html(
          '<i class="home blue icon"></i><i class="corner blue home icon"></i>'
        );

      helper.append('span').html('Neighborhood level data set');
    }

    if (c.sourcetable != '') {
      description
        .append('p')
        .classed('documentation-link', true)
        .append('a')
        .attr('href', '/data/' + c.sourcetable + '.html')
        .attr('target', '_blank')
        .html('(documentation)');
    }

    description.append('p').html(c.display_text);

    //Set it up to trigger the layer when title is clicked
    document
      .getElementById('filter-' + c.source)
      .addEventListener('click', clickCallback);
    function clickCallback() {
      //TODO this is hacked at the moment, need to restructure how a merged filter+overlay would work together
      //Currently hacking by assuming the overlay.name is the same as c.source (these are essentially the code name of the data set).
      //True only for ACS median rent, the demo data set.
      //This function is very similar to the overlay callback but w/ c.source instead of overlay.name
      if (c.data_level == 'zone') {
        var existingOverlayType =
          getState().overlaySet !== undefined
            ? getState().overlaySet[0].overlay
            : null;
        console.log('changing from ' + existingOverlayType + ' to ' + c.source);

        if (existingOverlayType !== c.source) {
          setState('overlayRequest', {
            overlay: c.source,
            activeLayer: getState().mapLayer[0],
          });
        } else {
          mapView.clearOverlay();
        }
      } else {
        mapView.clearOverlay();
      }
    } //end clickCallback

    return content;
  },

  categoricalFilterControl: function (component) {
    //Creates a new filterControl on the sidebar.
    //component is the variable of configuration settings pulled from dataChoices.js

    filterView.filterControl.call(this, component);
    var c = this.component;

    var contentContainer = filterView.setupFilter(c);

    var uiSelector = contentContainer
      .append('select')
      .classed('ui fluid search dropdown', true)
      .classed('dropdown-' + c.source, true) //need to put a selector-specific class on the UI to run the 'get value' statement properly
      .attr('multiple', ' ')
      .attr('id', c.source);

    //Add the dropdown menu choices
    for (var j = 0; j < c.options.length; j++) {
      uiSelector
        .append('option')
        .attr('value', c.options[j])
        .text(c.options[j]);
      //var select = document.getElementById(c.source);
    }

    $('#' + c.source).dropdown({ fullTextSearch: 'exact' });

    //Set callback for when user makes a change
    function makeSelectCallback(component) {
      return function () {
        var selectedValues = $(
          '.ui.dropdown.' + 'dropdown-' + component.source
        ).dropdown('get value');
        var specific_state_code = 'filterValues.' + component.source;
        setState(specific_state_code, selectedValues);
      };
    }
    var currentSelectCallback = makeSelectCallback(c);

    // Add the search box placeholder text
    var searchBox = contentContainer
      .select('input')
      .attr('placeholder', 'Type here to search.')
      .style('width', '100%');

    //TODO change this to a click event instead of any change
    $('.dropdown-' + c.source).change(currentSelectCallback);

    this.clear = function () {
      // 'restore defaults' as an argument of .dropdown resets the dropdown menu to its original state,
      // per the Semantic UI docs.
      $('.dropdown-' + c.source).dropdown('restore defaults');
    };

    this.isTouched = function () {
      return $('.dropdown-' + c.source).dropdown('get value').length > 0;
    };
  },

  searchFilterControl: function (component) {
    //Creates the search bar used with the name_addre field
    //Note, this is currently only configured to be used for one searchbar with the div id=searchbar
    //TODO fair amount of copy-modified code between this and the categorical one, would be good to consolidate
    filterView.filterControl.call(this, component);
    var c = this.component;
    var contentContainer = d3
      .select('#searchbar')
      .append('div')
      .attr('id', 'filter-content-' + c.source);

    var uiSelector = contentContainer
      .append('select')
      .classed('ui fluid multiple search selection dropdown', true)
      .classed('dropdown-' + c.source, true) //need to put a selector-specific class on the UI to run the 'get value' statement properly
      .attr('multiple', ' ')
      .attr('id', c.source + '-searchbar');

    //Add the dropdown menu choices
    for (var j = 0; j < c.options.length; j++) {
      uiSelector
        .append('option')
        .attr('value', c.options[j])
        .text(c.options[j]);
    }

    //Allow mid-string searches
    $('#' + c.source + '-searchbar').dropdown({
      fullTextSearch: 'exact',
      message: {
        noResults: 'No results found. Searching for address...',
      },

      onNoResults: _.debounce(function (value) {
        if (c.addressMarker) {
          c.addressMarker.remove();
        }
        $.ajax({
          dataType: 'json',
          url: `https://cors-anywhere.herokuapp.com/http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx/findLocation2?f=json&str=${value.toString(
            'base64'
          )}`,
          method: 'GET',
          success: function (data) {
            if (
              data.returnDataset &&
              data.returnDataset.Table1 &&
              data.returnDataset.Table1.length == 1
            ) {
              const address = data.returnDataset.Table1[0];
              const center = [address['LONGITUDE'], address['LATITUDE']];
              c.addressMarker = new mapboxgl.Marker()
                .setLngLat([address['LONGITUDE'], address['LATITUDE']])
                .addTo(mapView.map);
              mapView.map.flyTo({
                center,
                zoom: 18,
              });
            }
          },
        });

        return true;
      }, 2000),
    });

    //Change the icon
    d3.select('#searchbar')
      .select('.icon')
      .classed('dropdown', false)
      .classed('search', true);

    //Set callback for when user makes a change
    function makeSelectCallback(component) {
      return function () {
        var selectedValues = $(
          '.ui.dropdown.' + 'dropdown-' + component.source
        ).dropdown('get value');
        var specific_state_code = 'filterValues.' + component.source;

        setState(specific_state_code, selectedValues);
        if (component.addressMarker && selectedValues.length !== 0) {
          component.addressMarker.remove();
        }
      };
    }
    var currentSelectCallback = makeSelectCallback(c);

    // Add the search box placeholder text
    d3.select('#searchbar')
      .select('input')
      .attr('placeholder', 'Search for a project...')
      .style('width', '100%');

    //TODO change this to a click event instead of any change
    $('.dropdown-' + c.source).change(currentSelectCallback);

    this.clear = function () {
      $('.dropdown-' + c.source).dropdown('restore defaults');
    };

    this.isTouched = function () {
      return $('.dropdown-' + c.source).dropdown('get value').length > 0;
    };
  },

  locationFilterControl: function (component) {
    filterView.categoricalFilterControl.call(this, component);
    var c = this.component;
    var contentContainer = d3.select('#filter-content-' + c.source);
    var uiSelector = d3.select(c.source);

    console.log('Set up location filter');
    //TODO we will need to override the callback with a different callback that knows how to tell the state module the right zone type
  },

  updateLocationFilterControl: function (msg, data) {
    //Find out what layer is active. (using getState so we can subscribe to any event type)
    var layerType = getState()['mapLayer'][0];
    var choices = filterView.locationFilterChoices[layerType];

    //remove all existing choices
    d3.selectAll('#location option').remove();

    //Add the new ones in
    for (var j = 0; j < choices.length; j++) {
      d3.select('#location')
        .append('option')
        .attr('value', choices[j])
        .text(choices[j]);
    }
  },

  locationFilterChoices: {}, //populated based on data in the buildFilterComponents function

  components: dataChoices, //TODO replace all filterView.components references with dataChoices references after @ptgott merges in his changes

  setUpAssetToggler: function () {
    $('#assets-menu').accordion();
  },
  buildFilterComponents: function () {
    //We need to read the actual data to get our categories, mins, maxes, etc.
    var workingData = model.dataCollection['filterData'].objects;

    var parent = d3
      .select('#filter-components')
      .classed('ui styled fluid accordion', true); //semantic-ui styling

    $('#filter-components').accordion({
      exclusive: true,
      onOpen: function () {
        var difference =
          $(this).offset().top - $('#filter-components').offset().top;

        /*for debug
            console.log($( this ).offset().top);
            console.log('vs');
            console.log($('#filter-components').offset().top);
            console.log(difference);
            */
        // if the accordion content extend below the bounds of the #filters container
        $('#filter-components').animate(
          {
            scrollTop: $('#filter-components').scrollTop() + difference - 29,
          },
          500
        );
      },
    });

    //Add components to the navigation using the appropriate component type
    for (var i = 0; i < filterView.components.length; i++) {
      //console.log("building filter component: " + filterView.components[i].source);

      //Set up sliders
      if (filterView.components[i].component_type === 'continuous') {
        new filterView.continuousFilterControl(filterView.components[i]);
      }

      if (filterView.components[i].component_type === 'date') {
        new filterView.dateFilterControl(filterView.components[i]);
      }

      //note moved the .accordion settings out of for loop b/c only need to set once

      //set up categorical pickers
      if (filterView.components[i].component_type == 'categorical') {
        //First find the unique list of categories
        var result = [];
        for (var dataRow = 0; dataRow < workingData.length; dataRow++) {
          if (
            !result.includes(
              workingData[dataRow][filterView.components[i].source]
            )
          ) {
            result.push(workingData[dataRow][filterView.components[i].source]);
          }
        }
        result.sort();
        filterView.components[i]['options'] = result;

        new filterView.categoricalFilterControl(filterView.components[i]);
      }

      //search by name and address
      if (filterView.components[i].component_type == 'searchbar') {
        //First find the unique list of categories
        var result = [];
        for (var dataRow = 0; dataRow < workingData.length; dataRow++) {
          if (
            !result.includes(
              workingData[dataRow][filterView.components[i].source]
            )
          ) {
            result.push(workingData[dataRow][filterView.components[i].source]);
          }
        }
        result.sort();
        filterView.components[i]['options'] = result;

        new filterView.searchFilterControl(filterView.components[i]);
      }

      //set up location picker
      if (filterView.components[i].component_type == 'location') {
        //Create the object itself
        var location_options = ['First select a zone type'];
        filterView.components[i]['options'] = location_options;
        new filterView.locationFilterControl(filterView.components[i]);

        ///////////////////////////////////////////////////
        //Save the drop down choices for each location type for later use
        ///////////////////////////////////////////////////

        //Make empty lists for each type of dropdown
        mapView.initialLayers.forEach(function (layerDefinition) {
          filterView.locationFilterChoices[layerDefinition.source] = [];
        });

        //Iterate over the data itself and build a set of unique values
        for (var dataRow = 0; dataRow < workingData.length; dataRow++) {
          mapView.initialLayers.forEach(function (layerDefinition) {
            if (
              !filterView.locationFilterChoices[
                layerDefinition.source
              ].includes(workingData[dataRow][layerDefinition.source])
            ) {
              filterView.locationFilterChoices[layerDefinition.source].push(
                workingData[dataRow][layerDefinition.source]
              );
            }
          });
        }

        //Sort them alphabetically
        //TODO if we keep 'cluster 10' format, need to sort by number instead of purely alphabetically.
        Object.keys(filterView.locationFilterChoices).forEach(function (key) {
          filterView.locationFilterChoices[key].sort();
        });
      }
    } //end for loop. All components on page.

    //After all filter components are loaded, user is allowed to filter data
    setState('filterViewLoaded', true);
  },
  clearAllFilters: function () {
    for (var i = 0; i < filterView.filterControls.length; i++) {
      if (filterView.filterControls[i].isTouched()) {
        filterView.filterControls[i].clear();
        filterView.removeErrors(filterView.filterControls[i].component.source);
      }
    }
    filterView.indicateActivatedFilters();
  },
  clearLocationBasedFilters: function () {
    function isLocationBased(filterControl) {
      return filterControl.component.component_type === 'location';
    }
    function isZoneBased(filterControl) {
      return filterControl.component.data_level === 'zone';
    }
    for (var i = 0; i < filterView.filterControls.length; i++) {
      if (
        isLocationBased(filterView.filterControls[i]) &&
        filterView.filterControls[i].isTouched()
      ) {
        filterView.filterControls[i].clear();
      }
      /*
            if(isZoneBased(filterControl)){
                filterControl.adjustContentToCurrentMapLayer();
            }
            */
    }
  },
  clearAllButton: {
    init: function () {
      this.pill = document.createElement('div');
      this.pill.id = 'clearFiltersPillbox';
      this.pill.classList.add(
        'ui',
        'label',
        'transition',
        'visible',
        'clear-all'
      );

      this.site = document.getElementById('clear-pillbox-holder');

      this.site.insertBefore(this.pill, this.site.firstChild);
      this.pill.textContent = 'Clear all filters';

      this.pill.addEventListener('click', function () {
        filterView.clearAllFilters();
      });
      this.appendLabelPill();
    },
    appendLabelPill: function () {
      this.labelPill = document.createElement('div');

      this.labelPill.classList.add('label-all', 'ui', 'label');

      this.site = document.getElementById('clear-pillbox-holder');

      this.site.insertBefore(this.labelPill, this.site.firstChild);
      this.labelPill.textContent = 'Active Filters';
    },
    site: undefined,
    tearDown: function () {
      d3.select('.clear-all')
        .transition()
        .duration(750)
        .style('opacity', 0)
        .remove();
      d3.select('.label-all')
        .transition()
        .duration(750)
        .style('opacity', 0)
        .remove();
    },
  },
  addClearPillboxes: function (msg, data) {
    //Compare our activated filterValues (from the state module) to the list of all
    //possible filterControls to make a list containing only the activated filter objects.
    //filterValues = obj with keys of the 'source' data id and values of current setpoint
    //filterControls = list of objects that encapsulates the actual component including its clear() method
    var activeFilterControls = [];
    var filterValues = filterUtil.getFilterValues();
    for (var key in filterValues) {
      // An 'empty' filterValues array has a single element,
      // the value of nullsShown.
      if (filterValues[key][0].length != 0) {
        var control = filterView.filterControls.find(function (obj) {
          return obj['component']['source'] === key;
        });
        activeFilterControls.push(control);
      }
    }
    setState('numberOfFilters', activeFilterControls.length);
    var nullsShown = filterUtil.getNullsShown();
    Object.keys(nullsShown).forEach(function (key) {
      var control = filterView.filterControls.find(function (obj) {
        return obj['component']['source'] === key;
      });
      // The default nullsShown value is 'true'. If it's different than the default,
      // and the control hasn't already been added to activeFilterControls,
      // add the data choice's associated control to the array that we're using
      // to determine which filters to mark as altered.
      if (
        nullsShown[key][0] === false &&
        activeFilterControls.indexOf(control) === -1
      ) {
        activeFilterControls.push(control);
      }
    });

    //Use d3 to bind the list of control objects to our html pillboxes
    var holder = d3
      .select('#clear-pillbox-holder')
      .classed('force-hover', true);

    setTimeout(function () {
      holder.classed('force-hover', false);
    }, 2000);

    var allPills = holder
      .selectAll('.clear-single')
      .data(activeFilterControls, function (d) {
        return d.component.source;
      })
      .classed('not-most-recent', true);

    allPills
      .enter()
      .append('div')
      .attr('class', 'ui label transition hidden')
      .classed('clear-single', true)
      // Animate a label that 'flies' from the filter component
      // to the pillbox.
      .text(function (d) {
        return d['component']['display_name'];
      })
      .each(function (d) {
        var originElement = document.getElementById(
          'filter-content-' + d.component.source
        );
        var destinationElement = this;
        var flyLabel = document.createElement('div');
        flyLabel.textContent = this.textContent;
        flyLabel.classList.add(
          'ui',
          'label',
          'transition',
          'visible',
          'clear-single-flier'
        );
        var originRect = originElement.getBoundingClientRect();
        flyLabel.style.left = originRect.left + 'px';
        flyLabel.style.top = (originRect.top + originRect.bottom) / 2 + 'px';
        var flyLabelX = document.createElement('i');
        flyLabelX.classList.add('delete', 'icon');
        document.body.appendChild(flyLabel);
        flyLabel.appendChild(flyLabelX);

        // Change the 'top' and 'left' CSS properties of flyLabel,
        // triggering its CSS transition.
        window.setTimeout(function () {
          flyLabel.style.left =
            destinationElement.getBoundingClientRect().left + 'px';
          flyLabel.style.top =
            destinationElement.getBoundingClientRect().top + 'px';
        }, 1);

        // Remove flyLabel after its transition has elapsed.
        window.setTimeout(function () {
          flyLabel.parentElement.removeChild(flyLabel);
          destinationElement.classList.remove('hidden');
          destinationElement.classList.add('visible');
        }, 1500);
      })
      //Add pillbox click event to navigate to associated filter control
      .on('click', function (d) {
        var $accordion = $('#filter-' + d.component.source);
        if (!$accordion.hasClass('active')) {
          $accordion.click();
        } else {
          var difference =
            $accordion.offset().top - $('#filter-components').offset().top;
          $('#filter-components').animate(
            {
              scrollTop: $('#filter-components').scrollTop() + difference,
            },
            500
          );
        }
      })

      //Add the 'clear' x mark and its callback
      .append('i')
      .classed('delete icon', true)
      .on('click', function (d) {
        filterView.removeErrors(d.component.source);
        d.clear();
      });

    allPills.exit().transition().duration(750).style('opacity', 0).remove();
  },
  handleFilterClearance: function (message, data) {
    if (data === true) {
      filterView.clearAllButton.init();
    }
    if (data === false) {
      filterView.clearAllButton.tearDown();
    }
  },
  resetZoneFilters: function () {
    for (var i = 0; i < filterView.filterControls.length; i++) {
      var control = filterView.filterControls[i];
      if (control.component.data_level === 'zone') {
        control.rebuild();
      }
    }
  },
  indicateActivatedFilters: function () {
    //add/remove classes to the on-page elements that tell the users which filters are currently activated
    //e.g. the filter sidebar data name titles
    var filterValues = filterUtil.getFilterValues();
    var nullsShown = filterUtil.getNullsShown();
    var filterStateIsActive =
      getState()['anyFilterActive'] && getState()['anyFilterActive'][0] == true;

    var activeNullsShownKeys = Object.keys(nullsShown).filter(function (key) {
      return nullsShown[key][0] === false;
    });

    var activeFilterValuesKeys = Object.keys(filterValues).filter(function (
      key
    ) {
      return filterValues[key][0].length > 0;
    });

    var allActiveKeys = activeFilterValuesKeys.concat(activeNullsShownKeys);

    var noRemainingFilters = allActiveKeys.length === 0;

    Object.keys(filterValues).forEach(function (key) {
      var activated = allActiveKeys.indexOf(key) !== -1;
      d3.select('#filter-' + key).classed('filter-activated', activated);
    });

    if (noRemainingFilters && filterStateIsActive) {
      setState('anyFilterActive', false);
    }
    if (!noRemainingFilters && !filterStateIsActive) {
      setState('anyFilterActive', true);
    }
  },
  toggleSidebar: function (msg, data) {
    var sBar = document.getElementById(msg.replace('.', '-'));
    var leftRight = msg.indexOf('left') !== -1 ? 'left' : 'right';
    if (data === true) {
      sBar.classList.add('active'); // not supported in lte ie9
      document
        .getElementById('button-' + getState()['subNav.' + leftRight][0])
        .classList.add('active');
    } else {
      sBar.classList.remove('active'); // not supported in lte ie9
      document
        .getElementById('button-' + getState()['subNav.' + leftRight][0])
        .classList.remove('active');
    }
  },
  toggleSidebarState(sideBarMsg) {
    if (getState()[sideBarMsg] && getState()[sideBarMsg][0]) {
      setState(sideBarMsg, false);
    } else {
      setState(sideBarMsg, true);
    }
  },
  toggleSubNavButtons(msg, data) {
    var leftRight = msg.indexOf('left') !== -1 ? 'left' : 'right';
    if (
      getState()['sidebar.' + leftRight] &&
      getState()['sidebar.' + leftRight][0]
    ) {
      document
        .querySelectorAll('#' + leftRight + '-options .sub-nav-button')
        .forEach(function (button) {
          button.classList.remove('active');
        });
      document
        .querySelector('#' + leftRight + '-options #button-' + data)
        .classList.add('active');
    }
    document.querySelector('#' + data).classList.add('active');
    if (
      getState()['subNav.' + leftRight] &&
      getState()['subNav.' + leftRight][1]
    ) {
      document
        .querySelector('#' + getState()['subNav.' + leftRight][1])
        .classList.remove('active');
    }
  },
  expandSidebar: function (msg, data) {
    //data is the state of the expansion, either true or false

    //TODO this does not touch the fact that the sidebar can also be active or not. With current setup this does not cause issues but if controls are rearranged could be an issue
    d3.select('#sidebar-right').classed('expanded', data);
  },
};
