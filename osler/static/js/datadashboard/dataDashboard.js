//generate default date range and define global variables
let patientDataJson = null,
  ptCount = null,
  zipcodeColors = [],
  ethnicityColors = [],
  clinicDates = [],
  selectedEnd = [],
  selectedStart = [],
  selectedConditions = [],
  isConditionSelected = false,
  commonConditions = {},
  dateRanges = {},
  defaultDateRange = "All Time"; //options include: "Current/Latest Clinic", "This Month", "This Year", "All Time"

const urls = ["patientdata-json-datadashboard/","context-json-datadashboard/"]

async function fetchJsonData(urls) {
  try {
    var data = await Promise.all(
      urls.map(
        url =>
          fetch(url).then(
            (response) => response.json()
          )));
    return (data)

  } catch (error) {
      console.log(error)
      throw (error)
  }
}

//initial page load - display all-conditions data from latest clinic date
window.addEventListener("load", (event) => {
  (async() => {
    var responses = await fetchJsonData(urls)
    patientDataJson = responses[0]
    clinicDates = JSON.parse(responses[1].clinic_dates)
    numZipcodes = JSON.parse(responses[1].num_zipcodes)
    numEthnicities = JSON.parse(responses[1].num_ethnicities)

    zipcodeColors = makeColorArray(numZipcodes, "04009A");
    ethnicityColors = makeColorArray(numEthnicities, "206A5D");
    
    dateRangePicker()
    console.log(zipcodeColors)
    console.dir(patientDataJson)
    //load demographic data and generate charts  
    makeFilteredData("date");
    sortCommonConditions();
  
  })();
});

// load daterangepicker range buttons and build charts from a default date range
// https://www.daterangepicker.com/
function dateRangePicker(){
  //define custom date range buttons
  dateRanges["Current/Latest Clinic"] = [
    moment(clinicDates[clinicDates.length - 1]),
    moment(moment(clinicDates[clinicDates.length - 1]).add(1, "days").format()),
  ];
  dateRanges["This Month"] = [moment().startOf("month"), moment()];
  dateRanges["This Year"] = [moment().startOf("year"), moment()];
  dateRanges["All Time"] = [moment().subtract(20, "years"), moment()];
  selectedStart = dateRanges[defaultDateRange][0]._d;
  selectedEnd = dateRanges[defaultDateRange][1]._d;

  //date range picker logic
  $('input[name="daterange"]').daterangepicker(
    {
      locale: {
        format: gettext("MM/DD/YYYY"),
        separator: " - ",
        applyLabel: gettext("Apply"),
        cancelLabel: gettext("Cancel"),
        fromLabel: gettext("From"),
        toLabel: gettext("To"),
        customRangeLabel: gettext("Custom Range"),
        weekLabel: gettext("W"),
        daysOfWeek: [
          gettext("Su"),
          gettext("Mo"),
          gettext("Tu"),
          gettext("We"),
          gettext("Th"),
          gettext("Fr"),
          gettext("Sa"),
        ],
        monthNames: [
          gettext("January"),
          gettext("February"),
          gettext("March"),
          gettext("April"),
          gettext("May"),
          gettext("June"),
          gettext("July"),
          gettext("August"),
          gettext("September"),
          gettext("October"),
          gettext("November"),
          gettext("December"),
        ],
        firstDay: 1,
      },
      showDropdowns: true,
      ranges: dateRanges,
      linkedCalendars: false,
      alwaysShowCalendars: true,
      showCustomRangeLabel: false,
      startDate: moment(selectedStart),
      endDate: moment(selectedEnd),
      opens: "right",
    },
    //function called up date selection -> rebuild charts
    function (startDate, endDate) {
      selectedStart = startDate.format("YYYY-MM-DD");
      selectedEnd = endDate.format("YYYY-MM-DD");
      makeFilteredData("date");
      sortCommonConditions();  
      
    }
  );
};

//dynamically create buttons to display data related to conditions 
//only makes buttons for conditions represented in date range filtered data
function makeFilterByConditionButton(condition,index) {
  parent = document.getElementById("condition-filter-btns");

  conditionSelectorNode = document.createElement("li")
  conditionSelectorButton = document.createElement("button")
  conditionSelectorButton.setAttribute("class","btn btn-link btn-link-modern")
  conditionSelectorButton.setAttribute("id", condition + "-btn");
  parent.appendChild(conditionSelectorNode)
  conditionSelectorNode.appendChild(conditionSelectorButton)
  conditionSelectorButton.appendChild(document.createTextNode(condition));

  conditionSelectorButton.addEventListener("click", function(){
    selectedConditions = condition;
    isConditionSelected = true;
    let span = document.createTextNode(condition);
    document.getElementById("display-condition").childNodes[0].replaceWith(span);
    makeFilteredData("condition");
  });
};

// all conditions button event listener
document.getElementById("all-conditions-btn").addEventListener("click", function () {
  let span = document.createTextNode("Any Conditions");
  document.getElementById("display-condition").childNodes[0].replaceWith(span);
  isConditionSelected = false;
  makeFilteredData("condition");
});

function sortCommonConditions(){
  //map conditions to obj
  var commonConditionsPreSort = {};
  var filteredData
  commonConditions = {}
  //on first load, don't filter by condition
  if(Object.keys(commonConditions).length === 0){
    filteredData = filterPatientData(false)
  }
  else{
    filteredData = filterPatientData(true)
  }  
  if(Object.keys(filteredData).length != 0){
    Object.values(filteredData).map(function (e) {
      conditionsList = e.conditions;
      conditionsList.forEach((condition) => {
        if (!(condition in commonConditionsPreSort)) {
          commonConditionsPreSort[condition] = 1;
        } else {
          commonConditionsPreSort[condition] += 1;
        }
      });
    });
    // sort by most patients
    var sortable = [];
    for (var condition in commonConditionsPreSort) {
      sortable.push([condition, commonConditionsPreSort[condition]]);
    }
    sortable.sort(function (a, b) {
      return b[1] - a[1];
    });    
    sortable.forEach(
      (condition) => (commonConditions[condition[0]] = condition[1])
    );

    // default display all conditions
    if(Object.keys(selectedConditions).length === 0){
      selectedConditions = Object.keys(commonConditions);
    }
    Object.keys(commonConditions).length >= 5 ? $("#see-more-container").show() : $("#see-more-container").hide();
    $("#condition-filter-btns").empty();
    $("#more-conditions-btns").empty();
    for (var i = 0; i < Object.keys(commonConditions).length; i++) {
      makeFilterByConditionButton(Object.keys(commonConditions)[i],i);
    }
  }

  displayCommonConditionsStats(commonConditions)
};

function displayCommonConditionsStats(commonConditions){
  //append chronic condtion number counts to DOM
  var conditionsCountNode = document.getElementById("conditions-count")
  conditionsCountNode.innerHTML = Object.keys(commonConditions).length
  var counter = 1
  var dropdown = document.getElementById("conditions-dropdown");
  dropdown.innerHTML = '';
  for(const condition in commonConditions){
    var li = document.createElement('li')
    li.setAttribute("class","pt-1")
    dropdown.appendChild(li)

    var strong = document.createElement('strong')
    li.appendChild(strong)

    var spanNum = document.createElement('span')
    spanNum.setAttribute("class","ml-2")
    spanNum.setAttribute("id",counter+"-condition") 
    strong.appendChild(spanNum)

    var have = document.createElement('span')
    have.innerHTML = "&nbsp;patients with&nbsp;"
    li.appendChild(have)

    var spanName = document.createElement('span')
    spanName.setAttribute("class","mr-1")
    spanName.setAttribute("id",counter+"-condition-name")
    li.appendChild(spanName) 

    percentWithCondition = percentage(`${commonConditions[condition]}`, ptCount)
    conditionRankNode = document.getElementById(counter+"-condition")
    conditionRankNode.innerHTML = `${commonConditions[condition]}` + " (" + percentWithCondition + "%)"  
    conditionNameNode = document.getElementById(counter+"-condition-name")
    conditionNameNode.innerHTML = "<b>"+(`${condition}`)+"</b>"
    
    counter++
  }
}

function makeFilteredData(filterChangeOrigin) {
  var filteredData 

  //check if any data is selected if not - display error and open daterangepicker
  if (filterChangeOrigin == "date") {
    filteredData = filterPatientData(false);   
  } else if (filterChangeOrigin == "condition") {
    filteredData = filterPatientData(true);
  }

  //display error if no data to display
  if(Object.keys(filteredData).length == 0){  
    $("#flipFlop").modal();
  }
  else{
    displayPatientVisitStats(filteredData);
    displayLabsStats(filteredData);
    displayDrugsStats(filteredData);
    
    makeAgeChart(filteredData);
    makeGenderChart(filteredData);
    makeEthnicityChart(filteredData);
    makeZipcodeChart(filteredData);
    makeInsuranceChart(filteredData);

  }
};

function displayPatientVisitStats() {
  //append total workups to DOM
  wuCount = countWorkups(filteredData);
  wuCountText = document.createTextNode(wuCount);
  wuCountNode = document.getElementById("workups-count");
  $(wuCountNode).empty();
  wuCountNode.appendChild(wuCountText);

  //append unique patient count to DOM
  ptCount = Object.keys(filteredData).length;
  ptPercent = percentage(ptCount, wuCount);
  ptCountText = document.createTextNode(ptCount);
  ptCountNode = document.getElementById("unique-patient-count");
  $(ptCountNode).empty();
  ptCountNode.appendChild(ptCountText);

  //sort patients by number of workups (visits)
  var visits = {};
  visits["1"] = 0;
  visits["2"] = 0;
  visits["3"] = 0;
  visits["more"] = 0;

  Object.values(filteredData).map(function (e) {
    if (e.wu_dates.length > 3) {
      visits["more"] += 1;
    } else {
      for (const visitNum in visits) {
        if (e.wu_dates.length == parseInt(visitNum)) {
          visits[visitNum] += 1;
        }
      }
    }
  });

  //append sorted workup number counts to DOM
  for (const visitNum in visits) {
    percentVisits = percentage(visits[visitNum], ptCount);
    countNode = document.getElementById(visitNum + "-workup-count");
    countNode.innerHTML = visits[visitNum] + " (" + percentVisits + "%)";
  }
}

function displayLabsStats(filteredData) {
  var labs_count = {};
  var totalLabs = 0
  for (const [key, value] of Object.entries(patientDataJson)) {
    //check if lab was distributed to patient with the selected chronic condition if a condition is selected
    if (isConditionSelected == true) {
      if (value.conditions.includes(selectedConditions)) {
        for (lab in value.labs) {
          for (var i = 0; i < value.labs[lab].length; i++) {
            if (
              Date.parse(value.labs[lab][i]) >= Date.parse(selectedStart) &&
              Date.parse(value.labs[lab][i]) <= Date.parse(selectedEnd)
            ) {
              totalLabs += 1;
              if (!Object.keys(labs_count).includes(lab)) {
                labs_count[lab] = 1;
              } else {
                labs_count[lab] += 1;
              }
            }
          }
        }
      }
    } else {
      for (lab in value.labs) {
        for (var i = 0; i < value.labs[lab].length; i++) {
          if (
            Date.parse(value.labs[lab][i]) >= Date.parse(selectedStart) &&
            Date.parse(value.labs[lab][i]) <= Date.parse(selectedEnd)
          ) {
            totalLabs += 1
            if (!Object.keys(labs_count).includes(lab)) {
              labs_count[lab] = 1;
            } else {
              labs_count[lab] += 1;
            }
          }
        }
      }
    }
  }

  //append lab stats counts to DOM
  var labsCountNode = document.getElementById("labs-count");
  labsCountNode.innerHTML = String(totalLabs);
  var counter = 1;
  var dropdown = document.getElementById("labs-dropdown");
  $(dropdown).empty();
  for (const lab in labs_count) {
    var li = document.createElement("li");
    li.setAttribute("class", "pt-1");
    dropdown.appendChild(li);

    var spanName = document.createElement("span");
    spanName.setAttribute("class", "ml-1");
    spanName.setAttribute("id", counter + "-lab-name");
    li.appendChild(spanName);

    var spanNum = document.createElement("span");
    spanNum.setAttribute("class", "mr-1");
    spanNum.setAttribute("id", counter + "-lab-num");
    li.appendChild(spanNum);

    var conditionRankNode = document.getElementById(counter + "-lab-num");
    conditionRankNode.innerHTML = "<b>" + `${labs_count[lab]}` + "</b>";
    var conditionNameNode = document.getElementById(counter + "-lab-name");
    conditionNameNode.innerHTML = "<b>" + `${lab}:` + "&nbsp;</b>";

    counter++;
  }
}


function displayDrugsStats(filteredData) {
  var drugs_count = {};
  var totalDrugs = 0;
  for (const [key, value] of Object.entries(patientDataJson)) {
    //check if drug was distributed to patient with the selected chronic condition if a condition is selected
    if (isConditionSelected == true) {
      if (value.conditions.includes(selectedConditions)) {
        for (drug_dispense in value.drugs) {
          for (var i = 0; i < value.drugs[drug_dispense].length; i++) {
            if (
              Date.parse(value.drugs[drug_dispense][i]) >= Date.parse(selectedStart) &&
              Date.parse(value.drugs[drug_dispense][i]) <= Date.parse(selectedEnd)
            ) {
              totalDrugs += 1;
              if (!Object.keys(drugs_count).includes(drug_dispense)) {
                drugs_count[drug_dispense] = 1;
              } else {
                drugs_count[drug_dispense] += 1;
              }
            }
          }
        }
      }
    } else {
      for (drug_dispense in value.drugs) {
        for (var i = 0; i < value.drugs[drug_dispense].length; i++) {
          if (
            Date.parse(value.drugs[drug_dispense][i]) >= Date.parse(selectedStart) &&
            Date.parse(value.drugs[drug_dispense][i]) <= Date.parse(selectedEnd)
          ) {
            totalDrugs += 1;
            if (!Object.keys(drugs_count).includes(drug_dispense)) {
              drugs_count[drug_dispense] = 1;
            } else {
              drugs_count[drug_dispense] += 1;
            }
          }
        }
      }
    }
  }

  //append drug stats counts to DOM
  var drugsCountNode = document.getElementById("drugs-count");
  drugsCountNode.innerHTML = String(totalDrugs);
  var counter = 1;
  var dropdown = document.getElementById("drugs-dropdown");
  $(dropdown).empty();
  for (const drug_dispense in drugs_count) {
    var li = document.createElement("li");
    li.setAttribute("class", "pt-1");
    dropdown.appendChild(li);

    var spanName = document.createElement("span");
    spanName.setAttribute("class", "ml-1");
    spanName.setAttribute("id", counter + "-drug-name");
    li.appendChild(spanName);

    var spanNum = document.createElement("span");
    spanNum.setAttribute("class", "mr-1");
    spanNum.setAttribute("id", counter + "-drug-num");
    li.appendChild(spanNum);

    var conditionRankNode = document.getElementById(counter + "-drug-num");
    conditionRankNode.innerHTML = "<b>" + `${drugs_count[drug_dispense]}` + "</b>";
    var conditionNameNode = document.getElementById(counter + "-drug-name");
    conditionNameNode.innerHTML = "<b>" + `${drug_dispense}: ` + "&nbsp;</b>";

    counter++;
  }
}


function makeAgeChart(filteredData) {
  var sortedAges = [],
    ageRanges = [],
    ageLabels = [],
    ageDict = {};
  const ageStepSize = 10,
    maxAge = 100;

  // note: currently infants less than 1 years old are still counted and are displayed under the 1-ageStepSize range
  for (var i = 0; i < maxAge; i += ageStepSize) {
    ageDict = {};
    ageDict["key"] = i;
    ageDict["value"] = 0;
    ageRanges.push(ageDict);
    ageLabels.push(String(i + 1) + "-" + String(i + ageStepSize));
  }

  Object.values(filteredData).map(function (e) {
    ageRanges.forEach(function (range) {
      if (e.age > range["key"] && e.age <= range["key"] + ageStepSize)
        range["value"] += 1;
    });
  });

  ageRanges.forEach(function (range) {
    sortedAges.push(range["value"]);
  });

  var ageChartNode = removeOldChart("age-chart");
  var ageChart = ageChartNode.getContext("2d");
  return (chart = new Chart(ageChart, {
    responsive: "true",
    type: "bar",
    data: {
      labels: ageLabels,
      datasets: [
        {
          label: "# Patients",
          backgroundColor: "#FF9594",
          borderColor: "black",
          data: sortedAges,
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Age "
      },
      fullCornerRadius: false,
      cornerRadius: 15,
      scales: {
        yAxes: [
          {
            gridLines: {
              display: true,
              borderDash: [5, 5],
              lineWidth: 2,
              drawBorder: false,
              offsetGridLines: false,
            },
            ticks: {
              beginAtZero: true,
              maxTicksLimit: 5,
            },
            scaleLabel: {
              display: false,
            },
          },
        ],
        xAxes: [
          {
            gridLines: {
              display: false,
            },
            ticks: {
              beginAtZero: true,
            },
          },
        ],
      },
      legend: {
        display: false,
      },
    },
  }));
};

function makeGenderChart(filteredData) {
  //pass in date filtered data and then within each function extract the demographic data
  var genderData = {
    "Male": 0,
    "Female": 0,
    "Other": 0,
  };

  Object.values(filteredData).map(function (e) {
    for (var i = 0; i < Object.keys(genderData).length; i++) {
      if (e.gender == Object.keys(genderData)[i]) {
        genderData[Object.keys(genderData)[i]]++;
      }
    }
  });

  var genderChartNode = removeOldChart("gender-chart");
  genderChart = genderChartNode.getContext("2d");
  return (pieChart = new Chart(genderChart, {
    type: "pie",
    data: {
      labels: Object.keys(genderData),
      datasets: [
        {
          label: "Genders",
          backgroundColor: ["#80ABFC", "#FF9594", "#68D7D4"],
          data: Object.values(genderData),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,

      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: "Gender",
      },
    },
  }));
};

function makeEthnicityChart(filteredData) {
  var ethnicityData = {}

  Object.values(filteredData).map(function (e) {
    e.ethnicities.forEach(function (ethnicity) {
      if (!Object.keys(ethnicityData).includes(ethnicity)) {
        ethnicityData[ethnicity] = 1;
      }
      else{
        ethnicityData[ethnicity] += 1;
      }   
    });
  });

  var ethnicityChartNode = removeOldChart("ethnicity-chart");
  ethnicityChart = ethnicityChartNode.getContext("2d");
  return (pieChart = new Chart(ethnicityChart, {
    responsive: "true",
    type: "pie",
    data: {
      labels: Object.keys(ethnicityData),
      datasets: [
        {
          label: "Genders",
          backgroundColor: ethnicityColors,
          data: Object.values(ethnicityData),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,

      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: "Ethinicity",
      },
    },
  }));
};

function makeZipcodeChart(filteredData){
  var zipcodeData = {}
  Object.values(filteredData).map(function (e) {  
    if(e.zip_code == null){
      e.zip_code = "Homeless"
    }
    if (!Object.keys(zipcodeData).includes(e.zip_code)) {
      zipcodeData[e.zip_code] = 1;
    } else {
      zipcodeData[e.zip_code] += 1;
    }
  });

  var zipcodeChartNode = removeOldChart("zipcode-chart");
  zipcodeChart = zipcodeChartNode.getContext("2d");
  pieChart = new Chart(zipcodeChart, {
    responsive: "true",
    type: "pie",
    data: {
      labels: Object.keys(zipcodeData),
      datasets: [
        {
          label: "Zip Codes",
          backgroundColor: zipcodeColors,
          data: Object.values(zipcodeData),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,

      legend: {
        position: "bottom",
        align: "start",
        labels: {
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: "Zip Code",
      },
    },
  });
}

function makeInsuranceChart(filteredData) {
  //pass in date filtered data and then within each function extract the demographic data
  var insuranceData = {
    "true": 0,
    "false": 0,
    "null": 0,
  };

  Object.values(filteredData).map(function (e) {
    for (var i = 0; i < Object.keys(insuranceData).length; i++) {
      if (String(e.has_insurance) == Object.keys(insuranceData)[i]) {
        insuranceData[Object.keys(insuranceData)[i]]++;
      }
    }
  });

  var insuranceChartNode = removeOldChart("insurance-chart");
  insuranceChart = insuranceChartNode.getContext("2d");
  pieChart = new Chart(insuranceChart, {
    type: "pie",
    data: {
      labels: ["Yes","No","Not Answered"],
      datasets: [
        {
          label: "Insurance Status",
          backgroundColor: ["#80ABFC", "#FF9594", "#68D7D4"],
          data: Object.values(insuranceData),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: "Has Insurance",
      },
    },
  });
};

//
//vvv helper functions vvv
//

//filter all clinic data (jsondata) by selected condition and date range
function filterPatientData(filterByCondition){
  filteredData = {};
  for (const [key, value] of Object.entries(patientDataJson)) {    
    var filterOut = true;
    // check if condition matches selected condition
    if(filterByCondition){ 
      value.conditions.forEach(condition => {
        if (selectedConditions.includes(condition)) {
          //check if within selected date range
          value.wu_dates.map(function (d) {
            if (
              Date.parse(d) >= Date.parse(selectedStart) &&
              Date.parse(d) <= Date.parse(selectedEnd)
            ) {
              return (filterOut = false);
            }
          });
        }   
      })
    }
    else{
      value.wu_dates.map(function (d) {
        if (
          Date.parse(d) >= Date.parse(selectedStart) &&
          Date.parse(d) <= Date.parse(selectedEnd)                          
        ) {
          return (filterOut = false);
        }
      }); 
    }
    if (!filterOut) {
      filteredData[key] = value;
    }
  }
  return filteredData;
}

function removeOldChart(chartName){
  // and add a fresh canvas node
  var ChartParent = document.getElementById(chartName);
  $(ChartParent).empty()
  var ChartNode = document.createElement("canvas");
  ChartNode.setAttribute("id",chartName+"-canvas")
  ChartParent.appendChild(ChartNode)
  return ChartNode
};

function countWorkups(filteredData){
  wuCount = 0;
  for (const [key, value] of Object.entries(filteredData)) { 
    wuCount += value.wu_dates.length
  };
  return wuCount;
};

//returns a percentage of two numbers rounded to 1 decimal place, as a string
function percentage(portion, whole){
  return ((portion/whole)*100).toFixed(1);
}

function makeColorArray(num,startingCol) {
  var holderArr = []
  for (let i = 0; i < num; i++) {
    holderArr.push(lightenColor(startingCol, (100/num)*i));
  }
  return(holderArr)
  
}

function lightenColor (color, percent) {
  var num = parseInt(color, 16),
    amt = Math.round(2.55 * percent),
    R = (num >> 16) + amt,
    B = ((num >> 8) & 0x00ff) + amt,
    G = (num & 0x0000ff) + amt;

  return "#"+(
    0x1000000 +
    (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
    (B < 255 ? (B < 1 ? 0 : B) : 255) * 0x100 +
    (G < 255 ? (G < 1 ? 0 : G) : 255)
  )
    .toString(16)
    .slice(1);
};

