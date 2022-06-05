// JavaScript Document
const openInfoButtons = document.querySelectorAll('[data-popup-target]')
const closeInfoButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('info_overlay')

openInfoButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const info = document.querySelector(button.dataset.popupTarget)
		openInfo(info)
	})
})

overlay.addEventListener('click', () => {
  const infos = document.querySelectorAll('.info_popup.active')
  infos.forEach(info => {
    closeInfo(info)
  })
})


closeInfoButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const info = button.closest('.info_popup')
		closeInfo(info)
	})
})

function openInfo(info){
	if (info ==null) return
	info.classList.add('active')
	overlay.classList.add('active')
}

function closeInfo(info){
	if (info ==null) return
	info.classList.remove('active')
	overlay.classList.remove('active')
}


//for view pass
const openPassButtons = document.querySelectorAll('[data-pass-target]')
const closePassButtons = document.querySelectorAll('[data-close-button]')

openPassButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const pass = document.querySelector(button.dataset.passTarget)
		openPass(pass)
	})
})

closePassButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const pass = button.closest('.pass_popup')
		closePass(pass)
	})
})

function openPass(pass){
	if (pass ==null) return
	pass.classList.add('active')
	overlay.classList.add('active')
}

function closePass(pass){
	if (pass ==null) return
	pass.classList.remove('active')
	overlay.classList.remove('active')
}

//for view progress
const openProgressButtons = document.querySelectorAll('[data-progress-target]')
const closeProgressButtons = document.querySelectorAll('[data-close-button]')

openProgressButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const progress = document.querySelector(button.dataset.progressTarget)
		openProgress(progress)
	})
})

closeProgressButtons.forEach(button => {
	button.addEventListener('click', () =>{
		const progress = button.closest('.progress_popup')
		closeProgress(progress)
	})
})

function openProgress(progress){
	if (progress ==null) return
	progress.classList.add('active')
	overlay.classList.add('active')
}

function closeProgress(progress){
	if (progress ==null) return
	progress.classList.remove('active')
	overlay.classList.remove('active')
}

function functionRefresh() {
	//change the text
	var randomVal = Math.floor(Math.random() * 10);
	var tips = [
		['take a 5 minute brain break to re-energize. It helps!'], 
		['listen to your favorite song. It helps!'], 
		['get some fresh air to improve your mood.'], 
		['think of new wellness session on Yoi and make an appointment'], 
		['express gratitude to someone who made you smile'], 
		['close your eyes and take 30 deep breaths to rejuvenate'], 
		['solve a crossword puzzle or suduko or play a brain game'], 
		['tell your loved one how much they mean to you'], 
		['clean out the clutter at your workplace. Organize!'], 
		['desk-ercise - do a 5 minute stretching routine']
    ];
	document.getElementById('tip_text').innerHTML = tips[randomVal];
}
