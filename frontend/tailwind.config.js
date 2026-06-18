export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontSize: {
        '36-sb': ['36px', { lineHeight: '36px', fontWeight: '600' }],
        '24-sb': ['24px', { lineHeight: '30px', fontWeight: '600' }],
        '20-sb': ['20px', { lineHeight: '22px', fontWeight: '600' }],

        '16-sb': ['16px', { lineHeight: '22px', fontWeight: '600' }],
        '16-rg': ['16px', { lineHeight: '22px', fontWeight: '400' }],

        '14-sb': ['14px', { lineHeight: '22px', fontWeight: '600' }],
        '14-rg': ['14px', { lineHeight: '22px', fontWeight: '400' }],

        '12-sb': ['12px', { lineHeight: '20px', fontWeight: '600' }],
        '12-rg': ['12px', { lineHeight: '16px', fontWeight: '400' }],

        '10-sb': ['10px', { lineHeight: '16px', fontWeight: '600' }],
        '10-rg': ['10px', { lineHeight: '16px', fontWeight: '400' }],
      },
      colors: {
        primary: '#4B5FDC',
        primaryOpacity: '#C9CFF5',

        parking: '#FFB705',
        food: '#FF8A5C',
        label: '#F25637',
        button: '#F1F1F1',
        green: '#2D9E5F',
        red: '#E04444',

        login: '#F9FAFF',
        default: '#FDFDFF',
        neutral: '#F4F4F6',

        line1: '#E9E9E9',
        line2: '#DFDFDF',

        gray1: '#E1E1E1',
        gray2: '#969696',
        black1: '#333333',
      },
      borderRadius: {
        20: '20px',
        10: '10px',
        5: '5px',
        2: '2px',
      },
      boxShadow: {
        md: '3px 3px 10px 0 rgba(0,0,0,0.10)',
        sm: '0 2px 4px 0 rgba(0,0,0,0.25)',
        lg: '2px 2px 10px 5px rgba(0,0,0,0.10)',
        floating: '0 2px 10px 2px rgba(0,0,0,0.10)',
      },
      keyframes: {
        loading: {
          '0%': { width: '0%' },
          '100%': { width: '100%' },
        },
      },
      animation: {
        loading: 'loading 3s ease-in-out forwards',
      },
    },
  },
  plugins: [],
};
