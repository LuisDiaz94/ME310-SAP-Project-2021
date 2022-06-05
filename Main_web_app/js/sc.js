const sctimes= ['2022-06-02T14:42:00','2022-06-02T14:43:00','2022-06-02T14:44:00','2022-06-02T14:45:00'];
const scvalues= [2.1, 4.6, 2.1, 2.1];

const cht = document.getElementById('sc').getContext('2d');
const sc = new Chart(cht, {
    type: 'line',
	data: {
        labels: sctimes,
        datasets: [{
            label: 'Wellness level',
            data: [
				{x: sctimes[0], y: scvalues[0]},
				{x: sctimes[1], y: scvalues[1]},
				{x: sctimes[2], y: scvalues[2]},
				{x: sctimes[3], y: scvalues[3]}
			]
				,
            borderColor: [
                'rgba(138, 216, 70, 1)',
                'rgba(225, 92, 81, 1)',
                'rgba(138, 216, 70, 1)',
                'rgba(225, 92, 81, 1)'
            ],
            borderWidth: 1,
			tension: 0.4,
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
				},
			},
		},
        scales: {
            y: {
                beginAtZero: true,
				suggestedMin: 0,
                suggestedMax: 5,
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
				type:'time',
				time: {
					unit:'minute'
				},
				grid: {
					display: false,
					drawBorder: false,
				}
            },
        },
		
		
    }
	// plugins: ['chartjs-plugin-annotation']
});