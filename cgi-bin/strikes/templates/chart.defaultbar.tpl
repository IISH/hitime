{
   "elements":[
     {
       "type":      "bar",
       "alpha":     10,
       "colour":    "%%chartcolor%%",
       "font-size": 10,
	"values" :   [%%valueXurl%%]
     }
   ],
 
   "x_axis":{
     "stroke":1,
     "tick_height":200,
     "colour":"#909090",
     "grid_colour":"#00ff00",
     "offset":      50,
     "labels": {
      "labels": [%%labels%%]
      },
    },
 
   "y_axis":{
     "colour":      "#909090",
     "grid_colour": "#d0d0d0",
     "offset":      0,
     "max":         %%max%%,
	"steps": %%ystep%%
   }
}
 

