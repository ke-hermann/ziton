"""
__main__ module
"""


if __name__ == "__main__":
    # validate disk files
    # import order important to avoid loading from files
    # that haven't been verified yet
    import ziton.config as cfg

    cfg.validate_config_file()
    import ziton.database as db

    db.validate_database()
    if cfg.start_updated_enabled():
        db.build_database()

    from ziton.app import main

    main()
