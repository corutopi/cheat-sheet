import globals from 'globals';
import pluginJs from '@eslint/js';

export default [
  {
    languageOptions: { globals: globals.browser },
    extends: ['prettier'],
    rules: {
      indent: ['error', 4], // インデントを4に設定
    },
  },
  pluginJs.configs.recommended,
];
