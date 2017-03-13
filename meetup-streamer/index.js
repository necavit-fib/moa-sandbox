var meetup = require('meetup-stream')

var instances = 2;
var i = 0;

var rsvps = [];

meetup('rsvp', function (data) {
  console.log(i)
  i++;
  if (i == (instances - 1)) {
    console.log('Goodbye!');
    process.exit();
  }
});
