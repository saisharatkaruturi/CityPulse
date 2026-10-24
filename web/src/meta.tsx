// Runtime configuration from GET /api/meta: whether this deployment is a demo, and (only then) the
// fictional demo accounts. Nothing here is built into the bundle, so a production build never carries
// demo credentials.

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, type Meta } from './api';

interface MetaState { meta: Meta | null; failed: boolean }
const Ctx = createContext<MetaState>({ meta: null, failed: false });

export function MetaProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<MetaState>({ meta: null, failed: false });
  useEffect(() => {
    api<Meta>('/meta')
      .then((meta) => setState({ meta, failed: false }))
      .catch(() => setState({ meta: null, failed: true }));
  }, []);
  return <Ctx.Provider value={state}>{children}</Ctx.Provider>;
}

export const useMeta = () => useContext(Ctx);
