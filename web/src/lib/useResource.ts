// Loading state for one server resource, shared by every list and detail screen.
//
// * `reload()` really refetches; a second call while one is in flight joins it instead of firing twice.
// * A change of `key` aborts the old request, and a late response for an old key is ignored.
// * A failed refresh keeps the previous data and reports the error, so the screen can show it as stale.
// * `updatedAt` is the time the data actually arrived, never the time a button was pressed.

import { useCallback, useEffect, useRef, useState } from 'react';
import { isAbort } from '../api';

export interface Resource<T> {
  data: T | null;
  error: unknown;
  /** first load for this key */
  loading: boolean;
  /** a reload while data is already on screen */
  refreshing: boolean;
  updatedAt: Date | null;
  reload: () => Promise<void>;
  /** replace the data after a confirmed mutation, without a round trip */
  setData: (d: T) => void;
}

export function useResource<T>(key: string | null, fetcher: (signal: AbortSignal) => Promise<T>): Resource<T> {
  const [data, setDataState] = useState<T | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(key !== null);
  const [refreshing, setRefreshing] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;
  const keyRef = useRef(key);
  const inflight = useRef<{ key: string; promise: Promise<void>; ctrl: AbortController } | null>(null);

  const run = useCallback((k: string, hasData: boolean): Promise<void> => {
    if (inflight.current && inflight.current.key === k) return inflight.current.promise;
    inflight.current?.ctrl.abort();
    const ctrl = new AbortController();
    if (hasData) setRefreshing(true);
    else setLoading(true);
    const promise = fetcherRef.current(ctrl.signal)
      .then((d) => {
        if (keyRef.current !== k || ctrl.signal.aborted) return;
        setDataState(d);
        setError(null);
        setUpdatedAt(new Date());
      })
      .catch((e) => {
        if (isAbort(e) || keyRef.current !== k) return;
        setError(e);
      })
      .finally(() => {
        if (inflight.current?.ctrl === ctrl) inflight.current = null;
        if (keyRef.current === k) {
          setLoading(false);
          setRefreshing(false);
        }
      });
    inflight.current = { key: k, promise, ctrl };
    return promise;
  }, []);

  useEffect(() => {
    keyRef.current = key;
    if (key === null) {
      setLoading(false);
      return;
    }
    setDataState(null);
    setError(null);
    setUpdatedAt(null);
    void run(key, false);
    return () => {
      inflight.current?.ctrl.abort();
      inflight.current = null;
    };
  }, [key, run]);

  const reload = useCallback(() => (keyRef.current === null ? Promise.resolve() : run(keyRef.current, true)), [run]);
  const setData = useCallback((d: T) => {
    setDataState(d);
    setUpdatedAt(new Date());
  }, []);

  return { data, error, loading, refreshing, updatedAt, reload, setData };
}
