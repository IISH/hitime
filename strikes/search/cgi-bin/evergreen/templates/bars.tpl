{
  "title":{
    "text":  %%title%%,
    "style": "{font-size: 20px; color:#909090; font-family: Verdana; text-align: center;}"
  },

  "y_legend":{
    "text": %%amountname%%,
    "style": "{color: #909090; font-size: 12px;}"
  },

  "elements":[
    {
      "type":      "bar",
      "alpha":     0.5,
      "colour":    "#9933CC",
      "text":      "Page views",
      "font-size": 10,
      "values" :   [%%values%%]
    }
  ],

  "x_axis":{
    "stroke":1,
    "tick_height":10,
    "colour":"#909090",
    "grid_colour":"#00ff00",
    "labels": [%%labels%%]
   },

  "y_axis":{
    "stroke":      4,
    "tick_length": 3,
    "colour":      "#909090",
    "grid_colour": "#d0d0d0",
    "offset":      0,
    "max":         20
  }
}

