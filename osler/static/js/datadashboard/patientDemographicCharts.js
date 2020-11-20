var jsondata = null;

//generate default date range
var today = new Date(),
  todayStr = today.toLocaleDateString(),
  monthAgo = new Date(today.setMonth(today.getMonth() - 1)),
  monthAgoStr = monthAgo.toLocaleDateString();

//load json data sent to a url. Is this secure??
window.addEventListener("load", (event) => {
  fetch("send-json/")
    .then((res) => res.json())
    .then(
      (result) => {
        jsondata = result;
        console.log(jsondata);
        makeDateFilteredCharts(monthAgoStr, todayStr);
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
      startDate: monthAgoStr,
      endDate: todayStr,
      opens: "right",
    },
    function (start, end, label) {
      makeDateFilteredCharts(
        start.format("YYYY-MM-DD"),
        end.format("YYYY-MM-DD")
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
  console.log(dateFilteredData);
  ageChart(dateFilteredData);
  genderChart(dateFilteredData);
  ethnicityChart(dateFilteredData);
}

function ageChart(dateFilteredData) {
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

  var ctx = document.getElementById("htnAgeChart").getContext("2d");
  return (chart = new Chart(ctx, {
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
              display: false,
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

function genderChart(dateFilteredData) {
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

  var genderChart = document.getElementById("htnGenderChart").getContext("2d");
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
        text: "HTN Gender Distribution",
      },
    },
  }));
}

function ethnicityChart(dateFilteredData) {
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

  var ethnicityChart = document
    .getElementById("htnEthnicityChart")
    .getContext("2d");
  return (pieChart = new Chart(ethnicityChart, {
    responsive: "true",
    type: "doughnut",
    data: {
      labels: Object.keys(ethnicityData),
      datasets: [
        {
          label: "Genders",
          backgroundColor: [
            "#002b36",
            "#073642",
            "#586e75",
            "#657b83",
            "#839496",
            "#93a1a1",
            "#eee8d5",
            "#fdf6e3",
            "#662404",
          ],
          data: Object.values(ethnicityData),
        },
      ],
    },
    options: {
      legend: {
        labels: {
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: "HTN Ethnicity Distribution",
      },
    },
  }));
}
