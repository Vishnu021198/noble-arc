// magnify.js

document.addEventListener('DOMContentLoaded', function() {
    const magnify = document.querySelector('.magnify');
    const image = magnify.querySelector('img');
    
    magnify.addEventListener('mousemove', function(e) {
        const { left, top, width, height } = magnify.getBoundingClientRect();
        const x = e.clientX - left;
        const y = e.clientY - top;
        
        const offsetX = (x / width) * 100;
        const offsetY = (y / height) * 100;
        
        image.style.transformOrigin = `${offsetX}% ${offsetY}%`;
        image.style.transform = 'scale(2)';
    });
    
    magnify.addEventListener('mouseleave', function() {
        image.style.transformOrigin = 'center center';
        image.style.transform = 'scale(1)';
    });
});
