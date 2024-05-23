import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BotTradeListComponent } from './bot-trade-list.component';

describe('BotTradeListComponent', () => {
  let component: BotTradeListComponent;
  let fixture: ComponentFixture<BotTradeListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BotTradeListComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BotTradeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
