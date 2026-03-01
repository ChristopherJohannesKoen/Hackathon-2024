import React, { useState } from 'react';
import { Range, getTrackBackground } from 'react-range';

interface SnapSliderProps {
  values?: number[];
  onChange?: (value: number) => void;
}

const SnapSlider = ({ values = [1], onChange }: SnapSliderProps) => {
  const STEP = 1;
  const MIN = 1;
  const MAX = 6;

  const [value, setValue] = useState(values);

  const handleChange = (values: number[]) => {
    setValue(values);
    if (onChange) {
      onChange(values[0]);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        height: '100px',
        width: '300px',
        margin: '50px auto',
      }}
    >
      <Range
        values={value}
        step={STEP}
        min={MIN}
        max={MAX}
        onChange={handleChange}
        renderTrack={({ props, children }) => (
          <div
            {...props}
            style={{
              ...props.style,
              height: '36px',
              display: 'flex',
              width: '100%',
            }}
          >
            <div
              ref={props.ref}
              style={{
                height: '5px',
                width: '100%',
                borderRadius: '4px',
                background: getTrackBackground({
                  values: value,
                  colors: ['#548BF4', '#ccc'],
                  min: MIN,
                  max: MAX,
                }),
                alignSelf: 'center',
              }}
            >
              {children}
            </div>
          </div>
        )}
        renderThumb={({ props, isDragged }) => (
          <div
            {...props}
            style={{
              ...props.style,
              height: '0px',
              width: '0px',
              borderRadius: '0px',
              backgroundColor: '#FFF',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              boxShadow: '0px 2px 6px #AAA',
              border: 'solid 1px #ddd',
            }}
          >
            <div
              style={{
                height: '0px',
                width: '0px',
                backgroundColor: isDragged ? '#548BF4' : '#CCC',
              }}
            />
          </div>
        )}
      />
      <div style={{ marginTop: '20px', fontSize: '18px' }}>
        <TimeRangeDisplay value={value[0]} />
      </div>
    </div>
  );
};

const TimeRangeDisplay = ({ value }: { value: number }) => {
  const timeRanges = [
    '1 day',       // 1
    '4 days',      // 2
    '1 week',      // 3
    '1 month',     // 4
    '1 year',      // 5
    'Lifetime'     // 6
  ];

  return (
    <div>
      Current Range: {timeRanges[value - 1]}
    </div>
  );
};

export default SnapSlider;
