export const defaultConfig = {
  // API key
  apiKey: 'CAP-D895393EFA3F503D6F5A9DA2635276B31AA7D5B14AD257EF58FEE7372BA888DD',

  // Your Developer appId, Apply in dashboard's developer section
  appId: '',

  // Is the extension enabled by default or not
  useCapsolver: true,

  // Solve captcha manually
  manualSolving: false,

  // Captcha solved callback function name
  solvedCallback: 'captchaSolvedCallback',

  // Use proxy or not
  // If useProxy is true, then proxyType, hostOrIp, port, proxyLogin, proxyPassword are required
  useProxy: false,
  proxyType: 'http',
  hostOrIp: '',
  port: '',
  proxyLogin: '',
  proxyPassword: '',

  enabledForBlacklistControl: false, // Use blacklist control
  blackUrlList: [], // Blacklist URL list

  // Is captcha enabled by default or not
  enabledForRecaptcha: true,
  enabledForRecaptchaV3: true,
  enabledForImageToText: true,
  enabledForAwsCaptcha: true,
  enabledForCloudflare: true,

  // Task type: click or token
  reCaptchaMode: 'click',
  hCaptchaMode: 'click',

  // Delay before solving captcha
  reCaptchaDelayTime: 0,
  hCaptchaDelayTime: 0,
  textCaptchaDelayTime: 0,
  awsDelayTime: 0,

  // Number of repeated solutions after an error
  reCaptchaRepeatTimes: 10,
  reCaptcha3RepeatTimes: 10,
  hCaptchaRepeatTimes: 10,
  funCaptchaRepeatTimes: 10,
  textCaptchaRepeatTimes: 10,
  awsRepeatTimes: 10,

  // ReCaptcha V3 task type: ReCaptchaV3TaskProxyLess or ReCaptchaV3M1TaskProxyLess
  reCaptcha3TaskType: 'ReCaptchaV3TaskProxyLess',

  textCaptchaSourceAttribute: 'capsolver-image-to-text-source', // ImageToText source img's attribute name
  textCaptchaResultAttribute: 'capsolver-image-to-text-result', // ImageToText result element's attribute name

  textCaptchaModule: 'common', // ImageToText module

  showSolveButton: true, // Show solve button
};
