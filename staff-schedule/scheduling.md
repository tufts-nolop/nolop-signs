First, have the staff enter their availability in a when2meet.

Then, run this code in the JS console after loading the when2meet.

```js
// from https://gist.github.com/camtheman256/3125e18ba20e90b6252678714e5102fd?permalink_comment_id=4678586#gistcomment-4678586
function getCSV() {
  result = "Time," + PeopleNames.join(",")+"\n"; 
  for(let i = 0; i < AvailableAtSlot.length; i++) {
      let slot = $x(`string(//div[@id="GroupTime${TimeOfSlot[i]}"]/@onmouseover)`);
      slot = slot.match(/.*"(.*)".*/)[1];
      result += slot + ",";
      result += PeopleIDs.map(id => AvailableAtSlot[i].includes(id) ? 1 : 0).join(",");
      result+= "\n";
  }
  console.log(result);
  return result;
}
content = getCSV()

// Create element with <a> tag
const link = document.createElement("a");

// Create a blog object with the file content which you want to add to the file
const file = new Blob([content], { type: 'text/plain' });

// Add file content in the object URL
link.href = URL.createObjectURL(file);

// Add file name
link.download = "when2meet.csv";

// Add click event to <a> tag to save file.
link.click();
URL.revokeObjectURL(link.href);
```

This will create and download a CSV file with an availability column for each staff member.

Then just quickly write and execute some code that will assign shifts based on this data.

### Shift assignment algorithm

For each 15 minute shift, add up the number of staff available.
Sort the shifts by that value, so shifts with the least staff available are filled first.

For each shift, pick a staff member at random. If they are available and have been assigned less than 10 hours of shifts, assign them to the shift.

(Probably want a way to prioritize staff already assigned to adjacent shifts.)

Add 15 minutes to the staff member's total time.

It would be nice to be able to display the SVG shifts as they are populated, so we can see how the process works for debugging.

### Making the SVG image

Assign each staff member a fill color from the Tango color palette (at least 26 colors available if you use a few grays).

For each shift, insert a group of objects like this:

```xml
<g
   id="g100">
  <rect
     style="display:inline;fill:#edd400;fill-opacity:1;stroke-width:0.380055"
     id="rect100"
     width="14"
     height="76"
     x="32.611523"
     y="277.563" />
  <text
     xml:space="preserve"
     style="font-size:3.175px;line-height:1.25;font-family:sans-serif;display:inline;stroke-width:0.264583"
     x="35.583088"
     y="280.63756"
     id="text100"><tspan
       sodipodi:role="line"
       id="tspan100"
       style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:3.175px;font-family:sans-serif;-inkscape-font-specification:sans-serif;stroke-width:0.264583"
       x="35.583088"
       y="280.63756">CHET</tspan></text>
</g>
```

The rectangles should be 14 mm wide. For a shift of N hours, they should be (19 * N) - 1 mm tall, leaving 1 mm for a line at the end of a shift. 
