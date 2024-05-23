import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarketOpenComponent } from './market-open.component';

describe('MarketOpenComponent', () => {
  let component: MarketOpenComponent;
  let fixture: ComponentFixture<MarketOpenComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MarketOpenComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MarketOpenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
