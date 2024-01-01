from datetime import datetime, timedelta
import os
import pandas
import random
import time
import warnings

OUTPUT_FILE='schedule.svg'
INPUT_FILE='when2meet.csv'
MAX_WEEKLY_TIME_IN_MINUTES = 600 # 10 hours in minutes
MAX_SHIFT_LENGTH_IN_MINUTES = 300 # 5 hours in minutes
MAX_STAFF_ON_DUTY = 2
CLOSING_SHIFT = '10:45:00 PM'

shifts = pandas.DataFrame()

assignments = {} # example entry in dict of lists: 'Friday, 03:00:00 PM' | ['Arcadia', 'Aiden']

totals_by_person = {}

box_template='''
    <g
       id="{group_id}">
      <rect
         style="display:inline;fill:{box_color};fill-opacity:1;stroke-width:0.25"
         id="{rect_id}"
         width="{box_width}"
         height="{box_height}"
         x="{box_x}"
         y="{box_y}" />
      <text
         xml:space="preserve"
         style="font-size:3.175px;line-height:1.25;font-family:sans-serif;display:inline;stroke-width:0.25"
         x="{text_x}"
         y="{text_y}"
         {text_length}
         id="{text_id}"><tspan
           sodipodi:role="line"
           id="{tspan_id}"
           style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:3.175px;font-family:sans-serif;-inkscape-font-specification:sans-serif;stroke-width:0.25"
           x="{text_x}"
           y="{text_y}">{name}</tspan></text>
    </g>
'''

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

def add_box_to_schedule(f, dt, shift_length, column, name, color):
    #id=random.randint(0,9999999)
    id = str(int(time.time()*1000000))

    LEFT_MARGIN = 19.0
    HEIGHT_PER_MINUTE = 5.7/15
    TEXT_X_OFFSET = 0.5
    TEXT_Y_OFFSET = 3.0
    BOX_WIDTH = 13.0
    GUTTER = 0.25
    hours = dt.split(' ')[1].split(':')[0]
    minutes = dt.split(' ')[1].split(':')[1]
    box_y = HEIGHT_PER_MINUTE * 60 * int(hours) + HEIGHT_PER_MINUTE * int(minutes)
    day_of_week = dt.split(' ')[0]
    daycodes = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    box_x = LEFT_MARGIN + 2 * BOX_WIDTH * int(daycodes[day_of_week]) + GUTTER * int(daycodes[day_of_week]) + column * BOX_WIDTH
    if len(name) <= 5:
        text_length = ''
    else:
        text_length = 'textLength="12.5" lengthAdjust="spacingAndGlyphs"'

    f.write(box_template.format(group_id='g'+id, \
    	box_color=color, \
    	rect_id='rect'+id, \
    	box_width=str(BOX_WIDTH), \
    	box_height=str(shift_length*HEIGHT_PER_MINUTE), \
    	box_x=str(box_x), \
    	box_y=str(box_y), \
    	text_x=str(box_x + TEXT_X_OFFSET), \
    	text_y=str(box_y + TEXT_Y_OFFSET), \
        text_length=text_length, \
    	text_id='text'+id, \
    	tspan_id='tspan'+id, \
    	name=name))

def get_next_shift(shift_time): # pass in "Wednesday 11:45:00 am"
    day_of_week = shift_time.split(' ')[0] # strip off "Wednesday" and save it
    dt = datetime.strptime(' '.join(shift_time.split(' ')[1:]), "%I:%M:%S %p") # make a datetime from the "11:45:00 am"
    prev = dt + timedelta(minutes=15)
    return day_of_week + ' ' +  prev.strftime("%I:%M:%S %p") # put day and time back together

def select_worker(t):
    names = list(shifts.columns[1:-2]) # Hacky way of filtering out 'TIME', 'TOTAL_AVAILABLE', and 'STAFF_ON_DUTY'
    # if the last person can't keep working, pick someone else at random
    # keep picking at random until you find someone available
    # First, purge the list of potentials of people who have hit their weekly limit already.
    for name in names:
        if(totals_by_person[name] >= MAX_WEEKLY_TIME_IN_MINUTES):
            names.remove(name)
            print('Another shift would put {0} over the weekly limit'.format(name))
    try: # if you're already assigned to this shift, you can't be the second person assigned too.
        print(t)
        print(assignments[t][0])
        if(assignments[t][0]):
            names.remove(assignments[t][0])
    except:
        pass
    while(True):
        shift_length = 15
        if len(names) == 0:
            print('Nobody left for {0}'.format(t))
            return('NOBODY', shift_length)
        else:
            poss = random.choice(names)
        print(poss)
        if (shifts.loc[shifts['TIME'] == t][poss].values == 1): # find someone available
            print('{0} is a match to {1}'.format(poss, t))
            next_shift = get_next_shift(t)
            while(shifts.loc[shifts['TIME'] == next_shift][poss].values == 1): # extend the shift as long as availability and
                if(shift_length + 15 >= MAX_SHIFT_LENGTH_IN_MINUTES):          # max shift length allow
                    print('Max shift length exceeded: shift is {0} minutes.'.format(shift_length))
                    break
                if(next_shift not in shifts['TIME'].values):                       # unless next shift is already scheduled
                    print('next shift ({0}) already scheduled'.format(next_shift))
                    break
                if(totals_by_person[poss] + shift_length + 15 >= MAX_WEEKLY_TIME_IN_MINUTES):
                    names.remove(poss)
                    print('A shift longer than {0} would put {1} over the weekly limit'.format(shift_length, poss))
                    break
                shift_length += 15
                # print('shift_length is now {0}'.format(shift_length))
                if(check_still_open(next_shift)):
                    print('Checking {0}'.format(next_shift))
                    next_shift = get_next_shift(next_shift)
                else:
                    print('The time is {0}, which is equal to the last shift, {1}'.format(' '.join(next_shift.split(' ')[1:]), CLOSING_SHIFT))
                    break
            return (poss, shift_length)
        else:
            #print('{0} not available at {1}'.format(poss, t))
            #print(names)
            names.remove(poss)
            pass

def check_still_open(shift): # returns True if we're still open
    if 'AM' in shift:
        return True
    #shift_time = int(shift.split(' ')[1].split(':')[0]) # horrible hack to pull out hours digits
    print(shift)
    print(shift.split(' ')[1])
    shift_time = datetime.strptime(shift.split(' ')[1], '%H:%M:%S')
    close_time = datetime.strptime(CLOSING_SHIFT.split(' ')[0], '%H:%M:%S')
    #print(shift_time)
    if shift_time < close_time:
        return True
    else:
        return False

def add_shift_to_personal_total(name, shift_length):
    global totals_by_person
    totals_by_person[name] += shift_length

def log_shift(t, name):
        if t not in assignments:
            assignments[t] = [name]
        else:
            assignments[t].append(name)

def assign_shift(schedule, column, t):
        (name, shift_length) = select_worker(t)
        print(len(shifts.index))
        print('Assigning shift of length {0} at {1} to {2}'.format(shift_length, t, name))
        try:
            color = tango_colors[list(names).index(name)]
        except:
            color = '#FFFFFF' # white for nobody available
        add_box_to_schedule(schedule, t, shift_length, column, name, color)
        if(name != 'NOBODY'):
            add_shift_to_personal_total(name, shift_length)
        while(shift_length > 0):
            log_shift(t, name)
            print(shifts[shifts['TIME'] == t].index)
            shifts.drop(shifts[shifts['TIME'] == t].index, inplace=True)
            t = get_next_shift(t)
            shift_length -= 15

def write_shifts(schedule):
    global shifts
    times = shifts['TIME']
    for t in times:
        if t not in assignments:
            assign_shift(schedule, 0, t)        
    # instead of just doing this twice and manually incrementing column, this should be governed by MAX_STAFF_ON_DUTY
    # Next few lines are a hack to reload stuff because I don't understand how this code I wrote even works
    names = capped.columns[1:]
    shifts = capped.sort_values(by=['TOTAL_AVAILABLE'], kind='mergesort')
    times = shifts['TIME']
    print(assignments)
    print(times)
    for t in times:
        if len(assignments[t]) <= 1:
            assign_shift(schedule, 1, t)

def create_schedule():
    os.remove(OUTPUT_FILE)
    schedule = open(OUTPUT_FILE, 'w')
#    times = shifts['TIME']
    with open('schedule-header.xml') as head:
        schedule.write(head.read())
    with open('schedule-background.xml') as bg:
        schedule.write(bg.read())
    write_shifts(schedule) # the real work happens in here
    with open('schedule-footer.xml') as foot:
        schedule.write(foot.read())
    schedule.close()

df = pandas.read_csv(INPUT_FILE)
caps = dict(zip(df.columns, [s.split()[0].upper() for s in df.columns]))
capped = df.rename(columns=caps)
#print(capped)
names = capped.columns[1:]
print(names)
capped['TOTAL_AVAILABLE'] = df.sum(axis=1, numeric_only=True)
capped['STAFF_ON_DUTY'] = [0]*len(capped)
#print(capped.to_string())
shifts = capped.sort_values(by=['TOTAL_AVAILABLE'], kind='mergesort') # should also sort by time
print(shifts.to_string())

zeroes = [0]*len(names)
totals_by_person = dict(zip(names, zeroes))

create_schedule()

#print(assignments)
print(totals_by_person)