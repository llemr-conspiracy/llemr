var jsondata = null;

//generate default date range and define global variables that update with daterangepicker
var today = new Date(),
  selectedEnd = today.toLocaleDateString(),
  monthAgo = new Date(today.setMonth(today.getMonth() - 1)),
  selectedStart = monthAgo.toLocaleDateString(),
  allConditions = [],
  selectedConditions = [];

//initial page load - display all-conditions data
window.addEventListener("load", (event) => {
  fetch("all-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        console.log(jsondata)
        makeCommonConditionsChart();
        initializeHelper();
        makeFilteredCharts("condition");
      },
      (error) => {
        console.log("Error: " + error);
      }
    );
});

function makeCommonConditionsChart(){
  //map conditions to obj
  commonConditionsPreSort = {};
  Object.values(jsondata).map(function (e) {
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
  commonConditions = {};
  sortable.forEach(
    (condition) => (commonConditions[condition[0]] = condition[1])
  );

  allConditions = Object.keys(commonConditions)
  // default display all conditions
  selectedConditions = Object.keys(commonConditions);
  for (var i = 0; i < Object.keys(commonConditions).length; i++) {
    makeFilterByConditionButton(Object.keys(commonConditions)[i],i);
  }

  var commonConditionsChartNode = removeOldChart("conditions-chart-div");
  var commonConditionsChart = commonConditionsChartNode.getContext("2d");
  conditionsChart = new Chart(commonConditionsChart, {
    type: "horizontalBar",
    data: {
      labels: Object.keys(commonConditions).slice(0, 5),
      datasets: [
        {
          label: "# Patients with",
          backgroundColor: "#FF9594",
          borderColor: "black",
          data: Object.values(commonConditions).slice(0, 5),
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Most Common Conditions Seen",
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
  });
  // event listeners for filtering by displayed conditions
  canvas = document.getElementsByTagName("canvas")[0];
  canvas.onclick = function (evt) {
    var firstPoint = conditionsChart.getElementAtEvent(evt)[0];
    selectedConditions = [conditionsChart.data.labels[firstPoint._index]];
    makeFilteredCharts("condition");
  };
};

//date range picker
var dateRangePicker = $('input[name="daterange"]').daterangepicker(
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
      ranges: {
        Today: [moment(), moment()],
        "Last 7 Days": [moment().subtract(6, "days"), moment()],
        "This Month": [moment().startOf("month"), moment()],
        "This Year": [moment().startOf("year"), moment()],
        "All Time": [moment().subtract(20, "years"),moment()],
      },
      linkedCalendars: false,
      alwaysShowCalendars: true,
      startDate: selectedStart,
      endDate: selectedEnd,
      opens: "right",
    },
    function (startDate, endDate, label) {
      selectedStart = startDate.format("YYYY-MM-DD");
      selectedEnd = endDate.format("YYYY-MM-DD");      
      makeFilteredCharts("date");
    }
  );

function makeFilterByConditionButton(condition,index) {
  if(index <5){
    parent = document.getElementById("condition-filter-btns");
  }
  else{
    parent = document.getElementById("see-more-conditions");
  }
  conditionSelectorNode = document.createElement("li")
  conditionSelectorButton = document.createElement("button")
  conditionSelectorButton.setAttribute("class","btn btn-link btn-link-modern")
  conditionSelectorButton.setAttribute("id", condition + "-btn");
  parent.appendChild(conditionSelectorNode)
  conditionSelectorNode.appendChild(conditionSelectorButton)
  conditionSelectorButton.appendChild(document.createTextNode(condition));

  conditionSelectorButton.addEventListener("click", function (event) {
    selectedConditions = condition;
    // console.log(event.target.getAttribute("name"))
    console.log("listener "+ selectedConditions)
    let span = document.createTextNode("Displaying: "+condition);
    document.getElementById("display-condition").childNodes[0].replaceWith(span);
    makeFilteredCharts("condition");
  });
};
// all conditions button event listener
document.getElementById("all-conditions-btn").addEventListener("click", function () {
  let span = document.createTextNode("Displaying: All Conditions");
  document.getElementById("display-condition").childNodes[0].replaceWith(span);
  selectedConditions = allConditions;
  makeFilteredCharts("condition");
});

function filterData(jsondata){
  filteredData = {};
  for (const [key, value] of Object.entries(jsondata)) {
    var filterOut = true;
    // check if condition matches selected condition
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
      if (!filterOut) {
        filteredData[key] = value;
      }
    })
  }
  return filteredData;
}

function makeFilteredCharts(filterChangeOrigin) {
  filteredData = filterData(jsondata);
  if (filterChangeOrigin == "date") {
    //check if any data is selected if not - display error and open daterangepicker
    $('input[name="daterange"]').on(
      "apply.daterangepicker",
      function (ev, picker) {
        if (Object.keys(filteredData).length === 0) {
          picker.show();
          document.getElementById("date-select-error").style.display =
            "inline-block";
        } else {
          document.getElementById("date-select-error").style.display = "none";
          displayTotalPatients(filteredData);
          makeAgeChart(filteredData);
          makeGenderChart(filteredData);
          makeEthnicityChart(filteredData);
        }
      }
    );
  } else if (filterChangeOrigin == "condition") {
    displayTotalPatients(filteredData);
    makeAgeChart(filteredData);
    makeGenderChart(filteredData);
    makeEthnicityChart(filteredData);
  }
};

function displayTotalPatients(dateFilteredData){
  ptCount = document.createTextNode(Object.keys(dateFilteredData).length);
  ptCountNode = document.getElementById("unique-patient-count")
  $(ptCountNode).empty();
  ptCountNode.appendChild(ptCount);
};

//export currently displayed data to csv
document.getElementById("export-data").addEventListener("click", function () {
  // https://docs.djangoproject.com/en/3.1/ref/csrf/ passing csrf tokens via fetch api
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const request = new Request("export-csv/", {
    headers: { "X-CSRFToken": csrftoken, "Content-Type": "application/json" },
  });
  fetch(request, {
    method: "POST",
    mode: "same-origin",
    body: JSON.stringify(filteredData),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      // this fetch throws an error but still works so I'm just not logging it
    });
});

function makeAgeChart(dateFilteredData) {
  (ageStepSize = 10), (ageRanges = []), (ageLabels = []), (sortedAges = []);

  var ages = Object.values(dateFilteredData).map(function (e) {
    return e.age;
  });

  var maxAge = ages.reduce(function (a, b) {
    return Math.max(a, b);
  });

  // note: currently infants less than 1 years old are still counted and are displayed under the 1-ageStepSize range
  for (var i = 0; i < maxAge; i += ageStepSize) {
    ageDict = {};
    ageDict["key"] = i;
    ageDict["value"] = 0;
    ageRanges.push(ageDict);
    ageLabels.push(String(i + 1) + "-" + String(i + ageStepSize));
  }

  Object.values(dateFilteredData).map(function (e) {
    ageRanges.forEach(function (range) {
      if (e.age > range["key"] && e.age <= range["key"] + ageStepSize)
        range["value"] += 1;
    });
  });

  ageRanges.forEach(function (range) {
    sortedAges.push(range["value"]);
  });

  var ageChartNode = removeOldChart("ageChartDiv");
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
        text: "Age Distribution"
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

function makeGenderChart(dateFilteredData) {
  //pass in date filtered data and then within each function extract the demographic data
  var genderData = {
    Male: 0,
    Female: 0,
    Other: 0,
  };

  Object.values(dateFilteredData).map(function (e) {
    for (var i = 0; i < Object.keys(genderData).length; i++) {
      if (e.gender == Object.keys(genderData)[i]) {
        genderData[Object.keys(genderData)[i]]++;
      }
    }
  });

  var genderChartNode = removeOldChart("genderChartDiv");
  genderChart = genderChartNode.getContext("2d");
  return (pieChart = new Chart(genderChart, {
    type: "doughnut",
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
        text: "Gender Distribution",
      },
    },
  }));
};

function makeEthnicityChart(dateFilteredData) {
  var ethnicityData = {
    White: 0,
    "Black or African American": 0,
    "American Indian or Alaska Native": 0,
    Asian: 0,
    "Native Hawaiian or Other Pacific Islander": 0,
    "Hispanic or Latino": 0,
    Other: 0,
  };

  Object.values(dateFilteredData).map(function (e) {
    e.ethnicities.forEach(function (ethnicity) {
      for (var i = 0; i < Object.keys(ethnicityData).length; i++) {
        if (ethnicity == Object.keys(ethnicityData)[i]) {
          ethnicityData[Object.keys(ethnicityData)[i]]++;
        }
      }
    });
  });

  var ethnicityChartNode = removeOldChart("ethnicityChartDiv");
  ethnicityChart = ethnicityChartNode.getContext("2d");
  return (pieChart = new Chart(ethnicityChart, {
    responsive: "true",
    type: "doughnut",
    data: {
      labels: Object.keys(ethnicityData),
      datasets: [
        {
          label: "Genders",
          backgroundColor: [
            "#4875C7",
            "#80ABFC",
            "#68D7D4",
            "#AFEAE8",
            "#FF9594",
            "#FFBCBC",
            "#d6e4f8",
          ],
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
        text: "Ethinicity Distribution",
      },
    },
  }));
};


//helper functions
function removeOldChart(chartName){
  var ChartParent = document.getElementById(chartName);
  $(ChartParent).empty()
  var ChartNode = document.createElement("canvas");
  ChartParent.appendChild(ChartNode)
  return ChartNode
};

function initializeHelper(){
  datePickerError();
}

function datePickerError(){
  errorDiv = document.createElement("span");
  errorDiv.setAttribute("id", "date-select-error");
  errorDiv.style.display = "none";
  errorDiv.style.textAlign = "left";
  errorDiv.style.color = "#EB5B64";
  errorDiv.style.paddingRight = "40px";
  errorMsg = document.createTextNode(
    "Error: No data in selected date range"
  );
  datePickerNode = document.getElementsByClassName("drp-buttons")[0];
  datePickerNode.prepend(errorDiv);
  errorDiv.appendChild(errorMsg);
}