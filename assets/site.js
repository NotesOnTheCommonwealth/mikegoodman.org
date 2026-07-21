// Progressive disclosure: lists with data-first="N" show N entries + a Show all button.
document.querySelectorAll('ul.entries[data-first]').forEach(function(ul){
  var n = parseInt(ul.dataset.first, 10);
  var items = Array.prototype.slice.call(ul.children);
  if (items.length <= n) return;
  items.slice(n).forEach(function(li){ li.classList.add('hid'); });
  var btn = document.createElement('button');
  btn.className = 'showmore';
  var label = 'Show all ' + items.length + ' →';
  btn.textContent = label;
  ul.parentElement.insertBefore(btn, ul.nextSibling);
  btn.addEventListener('click', function(){
    if (ul.querySelector('.hid')) {
      items.forEach(function(li){ li.classList.remove('hid'); });
      btn.textContent = 'Show fewer ↑';
    } else {
      items.slice(n).forEach(function(li){ li.classList.add('hid'); });
      btn.textContent = label;
    }
  });
});

// Year filter (media page): chips with data-yr filter li[data-yr].
var chipbox = document.getElementById('yrchips');
if (chipbox) {
  var chips = chipbox.querySelectorAll('.chip');
  chips.forEach(function(c){
    c.addEventListener('click', function(){
      chips.forEach(function(x){ x.classList.remove('on'); });
      c.classList.add('on');
      var yr = c.dataset.yr;
      document.querySelectorAll('#medialist li').forEach(function(li){
        li.style.display = (yr === 'all' || li.dataset.yr === yr) ? '' : 'none';
      });
      var more = document.querySelector('#medialist ~ .showmore');
      if (more && yr !== 'all') more.style.display = 'none';
      else if (more) more.style.display = '';
      if (yr !== 'all') {
        document.querySelectorAll('#medialist li.hid').forEach(function(li){ li.classList.remove('hid'); });
      }
    });
  });
}
