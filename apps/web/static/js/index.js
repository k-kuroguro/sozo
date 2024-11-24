const createEventSource = () => {
   const es = new EventSource('/monitor');

   es.addEventListener('status_msg', function (event) {
      console.log(event.data);
      document.getElementById('score').innerHTML = `Status: ${event.data}`;
   });
   es.addEventListener('error_msg', function (event) {
      console.log(event.data);
      document.getElementById('score').innerHTML = `Error: ${event.data}`;
   });
   es.addEventListener('error', function (event) {
      console.log('Error', event);
   });
   es.addEventListener('open', function (event) { });

   return es;
};

es = createEventSource();

const fetchStatusByHour = async (targetHour) => {
   const response = await fetch(`/status/by-hour?target_hour=${targetHour}`);
   if (!response.ok) return [];
   return response.json();
}

const fetchStatusByDate = async (targetDate) => {
   const response = await fetch(`/status/by-date?target_date=${targetDate}`);
   if (!response.ok) return [];
   return response.json();
}

const calcAverageDate = (date1, date2) => {
   date1 = new Date(date1);
   date2 = new Date(date2);
   const time1 = date1.getTime();
   const time2 = date2.getTime();
   const averageTime = (time1 + time2) / 2;
   return new Date(averageTime);
}

const transformDataForChart = (data) => {
   let labels = [];
   let scores = [];
   let prev_end_time = undefined;
   for (let i = 0; i < data.length; i++) {
      const item = data[i];
      const start_time = item.start_time;
      const end_time = item.end_time;
      if (prev_end_time !== undefined && start_time !== prev_end_time) {
         labels.push(calcAverageDate(prev_end_time, start_time));
         scores.push(null);
      }
      labels.push(calcAverageDate(start_time, end_time));
      scores.push(item.overall_score);
      prev_end_time = end_time;
   }
   return { labels, scores };
}

const getRange = (time, by_hour) => {
   if (by_hour) {
      start = new Date(time);
      end = new Date(time);
      end.setHours(end.getHours() + 1);
      return {
         start: start,
         end: end
      };
   } else {
      start = new Date(time);
      end = new Date(time);
      end.setDate(end.getDate() + 1);
      return {
         start: start,
         end: end
      };
   }
}

const getXScales = (time, by_hour) => {
   const range = getRange(time, by_hour);
   if (by_hour) {
      return {
         title: {
            display: true,
            text: 'Time'
         },
         type: 'time',
         time: {
            parser: 'YYYY-MM-DDTHH:mm:ss',
            unit: 'minute',
            stepSize: 5,
            displayFormats: {
               'minute': 'mm'
            }
         },
         min: range.start,
         max: range.end
      };
   } else {
      return {
         title: {
            display: true,
            text: 'Time'
         },
         type: 'time',
         time: {
            parser: 'YYYY-MM-DDTHH:mm:ss',
            unit: 'hour',
            stepSize: 1,
            displayFormats: {
               'hour': 'HH'
            }
         },
         min: range.start,
         max: range.end
      };
   }
}

const renderChart = async (time, by_hour) => {
   try {
      const data = await (async () => {
         if (by_hour) {
            return await fetchStatusByHour(time);
         } else {
            return await fetchStatusByDate(time);
         }
      })();
      const { labels, scores } = transformDataForChart(data);
      const ctx = document.getElementById("statusChart").getContext("2d");
      const xScales = getXScales(time, by_hour);
      window.chart = new Chart(ctx, {
         type: 'line',
         data: {
            labels: labels,
            datasets: [{
               label: "Concentration Score",
               data: scores,
               borderColor: "rgba(75, 192, 192, 1)",
               backgroundColor: "rgba(75, 192, 192, 0.2)",
               borderWidth: 2,
               pointRadius: 0,
            }]
         },
         options: {
            responsive: true,
            plugins: {
               legend: {
                  display: true
               }
            },
            scales: {
               x: xScales,
               y: {
                  title: {
                     display: true,
                     text: 'Score'
                  },
                  min: 0,
                  max: 1
               }
            },
            spanGaps: false
         }
      });
   } catch (error) {
      console.error("Error rendering chart:", error);
   }
}


const renderWithParams = () => {
   if (window.chart) {
      window.chart.destroy();
   }
   const by_hour = document.getElementById("by-hour").checked;
   let datetime = document.getElementById("datetime").value;

   const split = datetime.split("T");
   if (by_hour) {
      datetime = `${split[0]}T${split[1][0]}${split[1][1]}:00:00`;
   } else {
      datetime = `${split[0]}T00:00:00`;
   }

   renderChart(datetime, by_hour);
}

document.getElementById("plotBtn").addEventListener("click", renderWithParams);
