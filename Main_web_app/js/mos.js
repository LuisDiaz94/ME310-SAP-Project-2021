const mostimes= [3.15,3.45,4.15,4.45];
const mosvalues= [0, 14, 5, 7];

function average1()
{
	return Math.trunc(mosvalues.reduce((a, b) => a + b, 0) / mosvalues.length);
}

const chrt = document.getElementById('mos').getContext('2d');
const mos = new Chart(chrt, {
    type: 'line',
	data: {
        labels: mostimes,
        datasets: [{
            label: 'Moments of arousal',
            data: mosvalues,
			fill: false,
			borderColor: 'rgb(75,192,192)',
			tension: 0.5,
		}],
		
    },
	options: {
		plugins: {
			legend:{
			display:false
			},
			
			autocolors:false,
			annotation: {
				annotations: {
					line1: {
						type: 'line',
						yMin: average1(),
						yMax: average1(),
						xMin: -0.25,
						xMax: 8.25,
						borderColor: 'rgba(80, 80, 80, 0.75)',
						borderWidth: 3,
						label: {
						enabled: true,
						content: 'average',
						position: 'end',
						xAdjust: 10,
						yAdjust: -10,
						backgroundColor: 'rgba(0, 0, 0, 0)',
							color: 'rgba(80, 80, 80, 0.9)',
							},
					},				
				},
			},
		},
        scales: {
            y: {
                beginAtZero: true,
				suggestedMin: 0,
                suggestedMax: 15,
				ticks:{
					display: false,
					drawTicks: false,
				},
				grid: {
					display: false,
					drawBorder: false,
					
				},
            },
            x: {
				grid: {
					display: false,
					drawBorder: false,
				}
            }
        }		
    }
     })
	// plugins: ['chartjs-plugin-annotation']