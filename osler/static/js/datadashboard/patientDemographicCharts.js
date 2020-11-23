var jsondata = null;

//generate default date range and define global variables that update with daterangepicker
var today = new Date(),
  globalEnd = today.toLocaleDateString(),
  monthAgo = new Date(today.setMonth(today.getMonth() - 1)),
  globalStart = monthAgo.toLocaleDateString();

//load json data from url on page load
window.addEventListener("load", (event) => {
  fetch("all-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        makeDateFilteredCharts(globalStart, globalEnd);
      },
      (error) => {
        console.log(error);
      }
    );
});

//load all conditions data
document.getElementById("all-btn").addEventListener("click", function () {
  let span = document.createElement("span");
  span.innerHTML = "Displaying: All Conditions";
  document.getElementById("display-condition").childNodes[0].replaceWith(span);

  fetch("all-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        makeDateFilteredCharts(globalStart, globalEnd);
      },
      (error) => {
        console.log(error);
      }
    );
});

//load hypertension data
document.getElementById("htn-btn").addEventListener("click", function () {
  let span = document.createElement("span");
  span.innerHTML = "Displaying: Hypertension";
  document.getElementById("display-condition").childNodes[0].replaceWith(span);

  fetch("hypertension-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        makeDateFilteredCharts(globalStart, globalEnd);
      },
      (error) => {
        console.log(error);
      }
    );
});

//load diabetes data
document.getElementById("dm-btn").addEventListener("click", function () {
  let span = document.createElement("span");
  span.innerHTML = "Displaying: Diabetes";
  document.getElementById("display-condition").childNodes[0].replaceWith(span);

  fetch("diabetes-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        makeDateFilteredCharts(globalStart, globalEnd);
      },
      (error) => {
        console.log(error);
      }
    );
});

//date range picker
$(function () {
  $('input[name="daterange"]').daterangepicker(
    {
      locale: {
        format: gettext("MM/DD/YYYY"),
        separator: " - ",
        applyLabel: gettext("Apply"),
        cancelLabel: gettext("Cancel"),
        fromLabel: gettext("From"),
        toLabel: gettext("To"),
        customRangeLabel: gettext("Custom"),
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
      },
      linkedCalendars: false,
      alwaysShowCalendars: true,
      startDate: globalStart,
      endDate: globalEnd,
      opens: "right",
    },
    function (startDate, endDate, label) {
      globalStart = startDate.format("YYYY-MM-DD");
      globalEnd = endDate.format("YYYY-MM-DD");
      makeDateFilteredCharts(
        startDate.format("YYYY-MM-DD"),
        endDate.format("YYYY-MM-DD")
      );
    }
  );
});

function makeDateFilteredCharts(startDate, endDate) {
  let dateFilteredData = {};
  for (const [key, value] of Object.entries(jsondata)) {
    var filterOut = true;
    value.wu_dates.map(function (d) {
      if (
        Date.parse(d) >= Date.parse(startDate) &&
        Date.parse(d) <= Date.parse(endDate)
      ) {
        return (filterOut = false);
      }
    });
    if (!filterOut) {
      dateFilteredData[key] = value;
    }
  }
  // console.log(dateFilteredData)
  makeAgeChart(dateFilteredData);
  makeGenderChart(dateFilteredData);
  makeEthnicityChart(dateFilteredData);
}

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
          label: "Hypertensive Age Ranges",
          backgroundColor: "#FF9594",
          borderColor: "black",
          data: sortedAges,
        },
      ],
    },
    options: {
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
}

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
        display: false,
        text: "Gender Distribution",
      },
    },
  }));
}

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
        display: false,
        text: "Ethinicity Distribution",
      },
    },
  }));
}


//helper functions
function removeOldChart(chartName){
  var ChartParent = document.getElementById(chartName);
  console.log(ChartParent)
  $(ChartParent).empty()
  var ChartNode = document.createElement("canvas");
  ChartParent.appendChild(ChartNode)
  return ChartNode
};
