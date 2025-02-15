from builder_refactor.cmd_builder import CLICommandBuilder

def main() -> None:
    parser = (
        CLICommandBuilder()
        .add_audio_process()
        .add_compress()
        .add_mix()
        .add_effects()
        .add_split()
        .add_adjust()
        .add_sync()
        .build()
    )
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
