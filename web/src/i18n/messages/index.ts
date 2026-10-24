// One flat dictionary per locale, merged from namespace files so each area of the app owns its words.
import * as auth from './auth';
import * as common from './common';
import * as landing from './landing';
import * as resident from './resident';
import * as staff from './staff';

export const en = { ...common.en, ...landing.en, ...auth.en, ...resident.en, ...staff.en };
export const te: Partial<Record<keyof typeof en, string>> = {
  ...common.te, ...landing.te, ...auth.te, ...resident.te, ...staff.te,
};
