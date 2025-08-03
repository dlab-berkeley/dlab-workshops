// Handle expandable prerequisites functionality
document.addEventListener('DOMContentLoaded', function() {
	document.addEventListener('click', function(e) {
		if (e.target.classList.contains('show-more-prereqs')) {
			e.preventDefault();
			const container = e.target.closest('.prerequisites-container');
			const initialView = container.querySelector('.d-flex');
			const fullView = container.querySelector('.all-prerequisites');
			
			initialView.classList.add('d-none');
			fullView.classList.remove('d-none');
		}
		
		if (e.target.classList.contains('show-less-prereqs')) {
			e.preventDefault();
			const container = e.target.closest('.prerequisites-container');
			const initialView = container.querySelector('.d-flex');
			const fullView = container.querySelector('.all-prerequisites');
			
			fullView.classList.add('d-none');
			initialView.classList.remove('d-none');
		}
	});
});