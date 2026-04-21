/**
 * Debounced action hook — prevents double-submits, rapid double-taps,
 * and accidental re-fires while the previous action is still in flight.
 *
 * Usage:
 *   const handleSubmit = useDebouncedAction(async () => {
 *     await api.post('/api/schemes/generate', payload);
 *   });
 *   ...
 *   <Button onPress={handleSubmit} disabled={handleSubmit.pending} />
 *
 * The returned function carries a `pending` boolean and an `error` (if the
 * last run threw). Consumers typically bind `pending` to the button's
 * `disabled` and/or loading-spinner state.
 */
import { useCallback, useRef, useState } from 'react';

type AnyArgs = unknown[];
type AsyncFn<A extends AnyArgs, R> = (...args: A) => Promise<R> | R;

export interface DebouncedAction<A extends AnyArgs, R> {
  (...args: A): Promise<R | undefined>;
  pending: boolean;
  error: unknown;
}

interface Options {
  /** Minimum gap between successive runs (ms). Default 800ms. */
  leadingGap?: number;
}

export function useDebouncedAction<A extends AnyArgs, R>(
  fn: AsyncFn<A, R>,
  { leadingGap = 800 }: Options = {}
): DebouncedAction<A, R> {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const lastRunAt = useRef(0);
  const inFlight = useRef(false);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const wrapped = useCallback(
    async (...args: A): Promise<R | undefined> => {
      const now = Date.now();
      if (inFlight.current) return undefined;
      if (now - lastRunAt.current < leadingGap) return undefined;
      lastRunAt.current = now;
      inFlight.current = true;
      setPending(true);
      setError(null);
      try {
        const result = await fnRef.current(...args);
        return result as R;
      } catch (e) {
        setError(e);
        throw e;
      } finally {
        inFlight.current = false;
        setPending(false);
      }
    },
    [leadingGap]
  );

  // Attach stateful flags to the callback so callers can wire disabled/loading.
  const debounced = wrapped as DebouncedAction<A, R>;
  debounced.pending = pending;
  debounced.error = error;
  return debounced;
}
