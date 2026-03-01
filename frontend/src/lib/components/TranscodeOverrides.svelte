<script lang="ts">
	import { onMount } from 'svelte';
	import type { Job, SettingsData, TranscoderConfig } from '$lib/types/arm';
	import { updateJobTranscodeConfig } from '$lib/api/jobs';
	import { fetchSettings } from '$lib/api/settings';

	interface Props {
		job: Job;
		onsaved?: () => void;
	}

	let { job, onsaved }: Props = $props();

	let loading = $state(true);
	let saving = $state(false);
	let feedback = $state<{ type: 'success' | 'error'; message: string } | null>(null);
	let tcConfig = $state<TranscoderConfig | null>(null);

	// Override form state
	let videoEncoder = $state('');
	let videoQuality = $state('');
	let audioEncoder = $state('');
	let subtitleMode = $state('');
	let handbrakePreset = $state('');
	let handbrakePreset4k = $state('');
	let handbrakePresetDvd = $state('');
	let handbrakePresetFile = $state('');
	let deleteSource = $state<'' | 'true' | 'false'>('');
	let outputExtension = $state('');

	function globalDefault(key: string): string {
		if (!tcConfig?.config) return '?';
		const val = tcConfig.config[key];
		if (val === null || val === undefined) return '?';
		if (typeof val === 'boolean') return val ? 'true' : 'false';
		return String(val);
	}

	onMount(async () => {
		try {
			const settings: SettingsData = await fetchSettings();
			tcConfig = settings.transcoder_config;
		} catch {
			tcConfig = null;
		} finally {
			loading = false;
		}

		// Pre-fill from existing overrides
		const o = job.transcode_overrides;
		if (o && typeof o === 'object') {
			videoEncoder = o.video_encoder != null ? String(o.video_encoder) : '';
			videoQuality = o.video_quality != null ? String(o.video_quality) : '';
			audioEncoder = o.audio_encoder != null ? String(o.audio_encoder) : '';
			subtitleMode = o.subtitle_mode != null ? String(o.subtitle_mode) : '';
			handbrakePreset = o.handbrake_preset != null ? String(o.handbrake_preset) : '';
			handbrakePreset4k = o.handbrake_preset_4k != null ? String(o.handbrake_preset_4k) : '';
			handbrakePresetDvd = o.handbrake_preset_dvd != null ? String(o.handbrake_preset_dvd) : '';
			handbrakePresetFile = o.handbrake_preset_file != null ? String(o.handbrake_preset_file) : '';
			deleteSource = o.delete_source != null ? (o.delete_source ? 'true' : 'false') : '';
			outputExtension = o.output_extension != null ? String(o.output_extension) : '';
		}
	});

	async function handleSave() {
		saving = true;
		feedback = null;
		try {
			const overrides: Record<string, unknown> = {};
			if (videoEncoder) overrides.video_encoder = videoEncoder;
			if (videoQuality) overrides.video_quality = Number(videoQuality);
			if (audioEncoder) overrides.audio_encoder = audioEncoder;
			if (subtitleMode) overrides.subtitle_mode = subtitleMode;
			if (handbrakePreset) overrides.handbrake_preset = handbrakePreset;
			if (handbrakePreset4k) overrides.handbrake_preset_4k = handbrakePreset4k;
			if (handbrakePresetDvd) overrides.handbrake_preset_dvd = handbrakePresetDvd;
			if (handbrakePresetFile) overrides.handbrake_preset_file = handbrakePresetFile;
			if (deleteSource) overrides.delete_source = deleteSource === 'true';
			if (outputExtension) overrides.output_extension = outputExtension;

			await updateJobTranscodeConfig(job.job_id, overrides);
			feedback = { type: 'success', message: Object.keys(overrides).length > 0 ? 'Overrides saved' : 'Overrides cleared' };
			onsaved?.();
		} catch (e) {
			feedback = { type: 'error', message: e instanceof Error ? e.message : 'Save failed' };
		} finally {
			saving = false;
		}
	}

	const inputClass =
		'rounded-lg border border-primary/25 bg-primary/5 px-3 py-1.5 text-sm text-gray-900 focus:border-primary focus:outline-hidden focus:ring-1 focus:ring-primary dark:border-primary/30 dark:bg-primary/10 dark:text-white';
	const labelClass = 'text-sm font-medium text-gray-700 dark:text-gray-300';
	const btnBase =
		'rounded-lg px-3 py-1.5 text-sm font-medium disabled:opacity-50 transition-colors';
</script>

{#if loading}
	<p class="text-sm text-gray-400">Loading transcoder settings...</p>
{:else if !tcConfig}
	<p class="text-sm text-gray-500 dark:text-gray-400">Transcoder not configured. Set up the transcoder in Settings to enable per-job overrides.</p>
{:else}
	<div class="space-y-4">
		<p class="text-xs text-gray-500 dark:text-gray-400">
			Override transcoder settings for this job only. Leave blank to use the global default.
		</p>

		<!-- Encoding -->
		<h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Encoding</h4>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
			<label class="space-y-1">
				<span class={labelClass}>Video Encoder</span>
				<select bind:value={videoEncoder} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('video_encoder')})</option>
					{#each tcConfig.valid_video_encoders ?? [] as enc}
						<option value={enc}>{enc}</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>Video Quality</span>
				<input
					type="number"
					bind:value={videoQuality}
					min="0"
					max="51"
					placeholder={globalDefault('video_quality')}
					class="{inputClass} w-full"
				/>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>Audio Encoder</span>
				<select bind:value={audioEncoder} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('audio_encoder')})</option>
					{#each tcConfig.valid_audio_encoders ?? [] as enc}
						<option value={enc}>{enc}</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>Subtitle Mode</span>
				<select bind:value={subtitleMode} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('subtitle_mode')})</option>
					{#each tcConfig.valid_subtitle_modes ?? [] as mode}
						<option value={mode}>{mode}</option>
					{/each}
				</select>
			</label>
		</div>

		<!-- Presets -->
		<h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Presets</h4>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
			<label class="space-y-1">
				<span class={labelClass}>HB Preset</span>
				<select bind:value={handbrakePreset} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('handbrake_preset')})</option>
					{#each tcConfig.valid_handbrake_presets ?? [] as p}
						<option value={p}>{p}</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>HB Preset (4K)</span>
				<select bind:value={handbrakePreset4k} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('handbrake_preset_4k')})</option>
					{#each tcConfig.valid_handbrake_presets ?? [] as p}
						<option value={p}>{p}</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>HB Preset (DVD)</span>
				<select bind:value={handbrakePresetDvd} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('handbrake_preset_dvd')})</option>
					{#each tcConfig.valid_handbrake_presets ?? [] as p}
						<option value={p}>{p}</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>Preset File</span>
				<select bind:value={handbrakePresetFile} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('handbrake_preset_file')})</option>
					{#each tcConfig.valid_preset_files ?? [] as f}
						<option value={f}>{f}</option>
					{/each}
				</select>
			</label>
		</div>

		<!-- Output -->
		<h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Output</h4>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
			<label class="space-y-1">
				<span class={labelClass}>Delete Source</span>
				<select bind:value={deleteSource} class="{inputClass} w-full">
					<option value="">(Global: {globalDefault('delete_source')})</option>
					<option value="true">Yes</option>
					<option value="false">No</option>
				</select>
			</label>

			<label class="space-y-1">
				<span class={labelClass}>Output Extension</span>
				<input
					type="text"
					bind:value={outputExtension}
					placeholder={globalDefault('output_extension')}
					class="{inputClass} w-full"
				/>
			</label>
		</div>

		<!-- Save -->
		<div class="flex items-center gap-2">
			<button
				onclick={handleSave}
				disabled={saving}
				class="{btnBase} bg-green-600 text-white hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600"
			>
				{saving ? 'Saving...' : 'Save Overrides'}
			</button>
			{#if feedback}
				<span
					class="text-xs {feedback.type === 'success'
						? 'text-green-600 dark:text-green-400'
						: 'text-red-600 dark:text-red-400'}"
				>
					{feedback.message}
				</span>
			{/if}
		</div>
	</div>
{/if}
