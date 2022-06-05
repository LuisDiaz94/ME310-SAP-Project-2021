// JavaScript Document
// Chart.register(chartjs-plugin-annotation);

const times= ['M', 'T', 'W', 'T', 'F', 'S'];
const values= [40, -16, 30, -30, 55];

function average()
{
	return Math.trunc(values.reduce((a, b) => a + b, 0) / values.length);
}

const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
	data: {
        labels: times,
        datasets: [{
            label: 'Wellness level',
            data: values,
            backgroundColor: [
				'rgba(138, 216, 70, 0.7)',
                'rgba(225, 92, 81, 0.7)',
                'rgba(138, 216, 70, 0.7)',
                'rgba(225, 92, 81, 0.7)',
                'rgba(225, 92, 81, 0.7)',
                'rgba(138, 216, 70, 0.7)',
				'rgba(138, 216, 70, 0.7)',
				'rgba(138, 216, 70, 0.7)',
				'rgba(225, 92, 81, 0.7)'
				
            ],
            borderColor: [
                'rgba(138, 216, 70, 1)',
                'rgba(225, 92, 81, 1)',
                'rgba(138, 216, 70, 1)',
                'rgba(225, 92, 81, 1)',
                'rgba(225, 92, 81, 1)',
                'rgba(138, 216, 70, 1)',
				'rgba(138, 216, 70, 1)',
				'rgba(138, 216, 70, 1)',
				'rgba(225, 92, 81, 1)'
            ],
            borderWidth: 1,
			borderRadius: 20,
			borderSkipped: false, 
			barPercentage: 0.7,
			
        }]
    },
    options: {
		plugins: {
			legend:{
			display:false
			},
			autocolors:false,
			annotation: {
				annotations: {
					line0: {
						type: 'line',
						yMin: 0,
						yMax: 0,
						borderColor: 'rgba(12,126, 207, 0.6)',
						borderWidth: 1,
					},
					line1: {
						type: 'line',
						yMin: average(),
						yMax: average(),
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
				suggestedMin: -100,
                suggestedMax: 100,
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
            },
        },
		
		
    }
	// plugins: ['chartjs-plugin-annotation']
});