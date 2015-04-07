{

  "title_":{
    "text":"Tooltip Hover",
    "style":"{font-size: 20px; font-family: Verdana; text-align: center;}"
  },

  "elements":[
    {
      "type":      "hbar",
      "tip":       "#left#",
      "colour":    "#9933CC",
      "text":      "",
      "font-size": 10,
      "values" :   [%%barvalues%%]
    }
  ],
  "x_axis":{
    "min":    0,
    "max":    %%max%%,
    "offset": false,
    "labels": {
      "labels": [%%Xvalues%%]
    }
  },
  "y_axis":{
    "offset":      true,
    "labels": [%%labels%%]
    
  },

  "tooltip":{
    "mouse": 1
  }
}
