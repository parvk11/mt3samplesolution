import argparse
import music_transcription_with_transformers
SAMPLE_RATE = 16000
SF2_PATH = music_transcription_with_transformers.SF2_PATH
import note_seq
import subprocess


def main():
    parser = argparse.ArgumentParser(description="MT3 Music Transcription Tool")
    parser.add_argument('--i', type=str, required=True, help="Path to the input audio file (e.g., .wav)")
    parser.add_argument('--o', type=str, default="output.mid", help="Path to save the transcribed MIDI file")
    
    args = parser.parse_args()

    # Run transcription

    command = ['gsutil', '-q', '-m', 'cp', 'gs://magentadata/soundfonts/SGM-v2.01-Sal-Guit-Bass-V1.3.sf2', '.']

    #Run the command
    try:
        subprocess.run(command, check=True)
        print("File copied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

    MODEL = "mt3" #@param["ismir2021", "mt3"]

    checkpoint_path = f'/checkpoints/{MODEL}/'

    music_transcription_with_transformers.load_gtag()

    music_transcription_with_transformers.log_event('loadModelStart', {'event_category': MODEL})
    inference_model = music_transcription_with_transformers.InferenceModel(checkpoint_path, MODEL)
    music_transcription_with_transformers.log_event('loadModelComplete', {'event_category': MODEL})

    #@title Upload Audio

    music_transcription_with_transformers.load_gtag()

    music_transcription_with_transformers.log_event('uploadAudioStart', {})
    audio = music_transcription_with_transformers.upload_audio(args.input, sample_rate=SAMPLE_RATE)
    music_transcription_with_transformers.log_event('uploadAudioComplete', {'value': round(len(audio) / SAMPLE_RATE)})

    note_seq.notebook_utils.colab_play(audio, sample_rate=SAMPLE_RATE)

    #@title Transcribe Audio
    #@markdown This may take a few minutes depending on the length of the audio file
    #@markdown you uploaded.

    music_transcription_with_transformers.load_gtag()

    music_transcription_with_transformers.log_event('transcribeStart', {
        'event_category': MODEL,
        'value': round(len(audio) / SAMPLE_RATE)
    })

    est_ns = inference_model(audio)

    music_transcription_with_transformers.log_event('transcribeComplete', {
        'event_category': MODEL,
        'value': round(len(audio) / SAMPLE_RATE),
        'numNotes': sum(1 for note in est_ns.notes if not note.is_drum),
        'numDrumNotes': sum(1 for note in est_ns.notes if note.is_drum),
        'numPrograms': len(set(note.program for note in est_ns.notes
                            if not note.is_drum))
    })

    note_seq.play_sequence(est_ns, synth=note_seq.fluidsynth,
                        sample_rate=SAMPLE_RATE, sf2_path=SF2_PATH)
    note_seq.plot_sequence(est_ns)

    #@title Download MIDI Transcription

    music_transcription_with_transformers.load_gtag()
    music_transcription_with_transformers.log_event('downloadTranscription', {
        'event_category': MODEL,
        'value': round(len(audio) / SAMPLE_RATE),
        'numNotes': sum(1 for note in est_ns.notes if not note.is_drum),
        'numDrumNotes': sum(1 for note in est_ns.notes if note.is_drum),
        'numPrograms': len(set(note.program for note in est_ns.notes
                            if not note.is_drum))
    })

    music_transcription_with_transformers.note_seq.sequence_proto_to_midi_file(est_ns, args.output)

if __name__ == "__main__":
    main()

    