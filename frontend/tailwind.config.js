export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontSize: {
        '36-sb': ['36px', { lineHeight: '36px', fontWeight: '600' }],
        '24-sb': ['24px', { lineHeight: '32px', fontWeight: '600' }],

        '16-sb': ['16px', { lineHeight: '24px', fontWeight: '600' }],

        '14-sb': ['14px', { lineHeight: '20px', fontWeight: '600' }],
        '14-rg': ['14px', { lineHeight: '20px', fontWeight: '400' }],

        '12-sb': ['12px', { lineHeight: '16px', fontWeight: '600' }],
        '12-rg': ['12px', { lineHeight: '16px', fontWeight: '400' }],

        '10-sb': ['10px', { lineHeight: '14px', fontWeight: '600' }],
        '10-rg': ['10px', { lineHeight: '14px', fontWeight: '400' }],
      },
      colors: {
        primary: '#4B5FDC',
        primaryOpacity: '#C9CFF5',

        food: '#FFB705',
        lodging: '#229EBC',
        label: '#F25637',
        button: '#F1F1F1',
        correct: '#2D9E5F',
        error: '#E04444',

        login: '#F9FAFF',
        default: '#FDFDFF',

        line1: '#E9E9E9',
        line2: '#DFDFDF',

        gray1: '#E1E1E1',
        gray2: '#969696',
        black1: '#333333',
      },
    },
  },
  plugins: [],
};
