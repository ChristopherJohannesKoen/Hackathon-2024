import React, { PureComponent } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface LinechartChartProps {
  data: any[];
}

 export function LinechartChart({data}: LinechartChartProps) {

    console.log(data);

  return (
     <AreaChart width={200} height={200} data={data} >
         <XAxis type="number" dataKey="usage_end_time" domain={['auto', 'auto']} tickFormatter={() => ''} axisLine = {false}  tickLine={false}/>
         <Area type="monotone" dataKey="usage_amount" stroke="#8884d8" fill="#8884d8" opacity={0.5}/>

        </AreaChart>
    // <h1>Graph here</h1>
  )
}
