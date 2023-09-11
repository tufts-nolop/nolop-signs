import time

box_template='''
    <g
       id="{group_id}">
      <rect
         style="display:inline;fill:{box_color};fill-opacity:1;stroke-width:0.380055"
         id="{rect_id}"
         width="{box_width}"
         height="{box_height}"
         x="{box_x}"
         y="{box_y}" />
      <text
         xml:space="preserve"
         style="font-size:3.175px;line-height:1.25;font-family:sans-serif;display:inline;stroke-width:0.264583"
         x="{text_x}"
         y="{text_y}"
         id="{text_id}"><tspan
           sodipodi:role="line"
           id="{tspan_id}"
           style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:3.175px;font-family:sans-serif;-inkscape-font-specification:sans-serif;stroke-width:0.264583"
           x="{text_x}"
           y="{text_y}">{name}</tspan></text>
    </g>
'''

#id=random.randint(0,9999999)
id = str(int(time.time()*1000000))

HOUR_HEIGHT = 25
TEXT_Y_OFFSET = 3.0
shift_length = 3
box_y = 277.5

tango_colors = [ \
    '#edd400', \
    '#fce94f', \
    '#c4a000', \
    '#8ae234', \
    '#73d216', \
    '#4e9a06', \
    '#fcaf3e', \
    '#f57900', \
    '#ce5c00', \
    '#729fcf', \
    '#3465a4', \
    '#204a87', \
    '#ad7fa8', \
    '#75507b', \
    '#5c3566', \
    '#e9b96e', \
    '#c17d11', \
    '#cc0000', \
    '#8f5902', \
    '#ef2929', \
    '#a40000', \
    '#eeeeec', \
    '#babdb6', \
    '#888a85', \
    '#555753', \
    '#000000']

print(box_template.format(group_id='g'+id, \
	box_color=tango_colors[0], \
	rect_id='rect'+id, \
	box_width='14', \
	box_height=str(shift_length*HOUR_HEIGHT), \
	box_x='32.611523', \
	box_y=str(box_y), \
	text_x='35.583088', \
	text_y=str(box_y + TEXT_Y_OFFSET), \
	text_id='text'+id, \
	tspan_id='tspan'+id, \
	name='CHET'))