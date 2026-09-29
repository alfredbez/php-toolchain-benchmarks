<?php

declare(strict_types=1);

namespace CarthageSoftware\ToolChainBenchmarks\Profiler\Internal;

use Psl\Iter;
use Psl\Regex;
use Psl\Shell;
use Psl\Str;
use Psl\Vec;

/**
 * Stop a timed-out command and its workers before starting the next measurement.
 *
 * @internal
 */
final readonly class ProcessTreeTerminator
{
    /**
     * @param resource $process
     */
    public static function terminate($process): void
    {
        $pid = proc_get_status($process)['pid'];

        try {
            $output = Shell\execute('ps', ['-eo', 'pid,ppid']);
        } catch (Shell\Exception\FailedExecutionException) {
            $output = '';
        }

        /** @var array<int, list<int>> $children */
        $children = [];
        foreach (Str\split(Str\trim($output), "\n") as $line) {
            $parts = Regex\split(Str\trim($line), '/\s+/');
            if (Iter\count($parts) < 2) {
                continue;
            }

            $child = (int) $parts[0];
            $parent = (int) $parts[1];
            if ($child > 0) {
                $children[$parent][] = $child;
            }
        }

        $queue = [$pid];
        $descendants = [];
        while ($queue !== []) {
            $parent = array_shift($queue);
            foreach ($children[$parent] ?? [] as $child) {
                $descendants[] = $child;
                $queue[] = $child;
            }
        }

        foreach (Vec\reverse($descendants) as $child) {
            if (!function_exists('posix_kill')) {
                continue;
            }
            posix_kill($child, SIGKILL);
        }

        proc_terminate($process, 9);
        proc_close($process);
    }
}
